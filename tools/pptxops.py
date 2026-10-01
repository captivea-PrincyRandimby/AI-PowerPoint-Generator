"""Opérations bas niveau : copie de slides / formes entre présentations (avec images,
SmartArt, graphiques, liens), suppression de slides, remplissage de zones.

Utilisé par build.py (transformation) et reuse / tracking (bibliothèque unique_slides).
"""
from __future__ import annotations

import copy
import hashlib
import re

from lxml import etree
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.parts.image import ImagePart
from pptx.util import Emu, Inches

from common import (A, OLD_VIOLETS, P, R, RED2, charte_gradient, is_hidden, iter_shapes,
                    notes_text, set_hidden, set_notes)

SKIP_RELS = {RT.SLIDE_LAYOUT, RT.NOTES_SLIDE}
DGM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"


# --------------------------------------------------------------------------
# Copie de parties (images, SmartArt, graphiques, embeddings…)
# --------------------------------------------------------------------------
class PartCopier:
    """Copie des parties d'un package source vers un package destination (avec cache)."""

    def __init__(self, dst_package):
        self.pkg = dst_package
        self.cache = {}          # id(part source) -> part destination
        # noms réservés / images connues PARTAGÉS par tous les copieurs du même package
        # (une partie copiée n'est pas encore reliée au graphe quand on nomme ses enfants)
        if not hasattr(dst_package, "_ppt_reserved"):
            dst_package._ppt_reserved = set()
            dst_package._ppt_images = {hashlib.sha1(p.blob).hexdigest(): p
                                       for p in dst_package.iter_parts() if isinstance(p, ImagePart)}
        self.reserved = dst_package._ppt_reserved
        self.images = dst_package._ppt_images

    def _next_partname(self, src_partname: str) -> PackURI:
        base, ext = src_partname.rsplit(".", 1)
        base = re.sub(r"\d+$", "", base)
        existing = {str(p.partname) for p in self.pkg.iter_parts()} | self.reserved
        n = 1
        while f"{base}{n}.{ext}" in existing:
            n += 1
        name = f"{base}{n}.{ext}"
        self.reserved.add(name)
        return PackURI(name)

    def copy(self, src_part):
        key = id(src_part)
        if key in self.cache:
            return self.cache[key]
        if isinstance(src_part, ImagePart):
            sha = hashlib.sha1(src_part.blob).hexdigest()
            if sha not in self.images:
                self.images[sha] = ImagePart(self._next_partname(str(src_part.partname)),
                                             src_part.content_type, self.pkg, src_part.blob)
            self.cache[key] = self.images[sha]
            return self.images[sha]
        new = Part(self._next_partname(str(src_part.partname)), src_part.content_type,
                   self.pkg, src_part.blob)
        self.cache[key] = new
        mapping = {}
        for rId, rel in src_part.rels.items():
            if rel.is_external:
                mapping[rId] = new.relate_to(rel.target_ref, rel.reltype, is_external=True)
            elif rel.reltype not in SKIP_RELS:
                mapping[rId] = new.relate_to(self.copy(rel.target_part), rel.reltype)
        if mapping:
            new._blob = _remap_blob(src_part.blob, mapping)
        return new


def _remap_blob(blob: bytes, mapping: dict) -> bytes:
    return re.sub(rb'"(rId\d+)"',
                  lambda m: b'"' + mapping.get(m.group(1).decode(), m.group(1).decode()).encode() + b'"',
                  blob)


def remap_element_rels(el, src_part, dst_part, copier: PartCopier):
    """Réécrit tous les r:* d'un élément copié pour pointer vers des relations du dst."""
    slide_map = {}

    def map_rid(rid):
        if rid in slide_map:
            return slide_map[rid]
        if rid not in src_part.rels:
            return rid
        rel = src_part.rels[rid]
        if rel.is_external:
            new = dst_part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            new = dst_part.relate_to(copier.copy(rel.target_part), rel.reltype)
        slide_map[rid] = new
        return new

    drop = []
    for node in el.iter():
        for attr, val in list(node.attrib.items()):
            if attr.startswith(R) and val.startswith("rId"):
                if val in src_part.rels and src_part.rels[val].reltype == RT.SLIDE:
                    drop.append(node)  # lien interne vers une autre slide : non transposable
                    continue
                node.set(attr, map_rid(val))
    for node in drop:
        if node.getparent() is not None:
            node.getparent().remove(node)
    # SmartArt : la partie "data" référence le dessin (diagramDrawing) via un relId
    # de la SLIDE (attribut sans namespace) -> copier et corriger.
    for gd in el.iter(A + "graphicData"):
        if gd.get("uri") != DGM_URI:
            continue
        for rel_ids in gd:
            dm = rel_ids.get(R + "dm")
            if not dm:
                continue
            data_part = dst_part.rels[dm].target_part
            blob = data_part.blob
            m = re.search(rb'relId="(rId\d+)"', blob)
            if m:
                old = m.group(1).decode()
                new = map_rid(old)
                data_part._blob = blob.replace(m.group(0), f'relId="{new}"'.encode())
    return slide_map


# --------------------------------------------------------------------------
# Slides
# --------------------------------------------------------------------------
def _layout_key(name: str) -> str:
    # "1_Main Title" == "Main Title" (préfixe ajouté par PowerPoint lors des copies de masques)
    return re.sub(r"^\d+_", "", re.sub(r"\s+", " ", name.strip().lower()))


def layout_by_name(prs, name: str):
    wanted = name.strip().lower()
    for lay in prs.slide_layouts:
        if lay.name.strip().lower() == wanted:
            return lay
    for lay in prs.slide_layouts:
        if _layout_key(lay.name) == _layout_key(name):
            return lay
    names = [l.name for l in prs.slide_layouts]
    raise KeyError(f"Masque introuvable : {name!r}. Disponibles : {names}")


def clear_placeholders(slide, keep=()):
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx not in keep:
            ph._element.getparent().remove(ph._element)


def clone_slide(src_slide, dst_prs, copier: PartCopier | None = None, layout_name=None):
    """Copie intégrale d'une slide (formes, fond, images, SmartArt, notes, état masqué).

    Le masque est retrouvé par NOM dans la présentation destination (même template).
    """
    copier = copier or PartCopier(dst_prs.part.package)
    lname = layout_name or src_slide.slide_layout.name
    try:
        layout = layout_by_name(dst_prs, lname)
    except KeyError:
        layout = layout_by_name(dst_prs, "Standard - Empty")
    new = dst_prs.slides.add_slide(layout)
    clear_placeholders(new)
    src_tree = src_slide.shapes._spTree
    dst_tree = new.shapes._spTree
    for child in src_tree:
        if child.tag in (P + "nvGrpSpPr", P + "grpSpPr"):
            continue
        el = copy.deepcopy(child)
        dst_tree.append(el)
        remap_element_rels(el, src_slide.part, new.part, copier)
    # fond de slide
    src_bg = src_slide._element.find(f"{P}cSld/{P}bg")
    if src_bg is not None:
        bg = copy.deepcopy(src_bg)
        remap_element_rels(bg, src_slide.part, new.part, copier)
        csld = new._element.find(P + "cSld")
        old = csld.find(P + "bg")
        if old is not None:
            csld.remove(old)
        csld.insert(0, bg)
    set_hidden(new, is_hidden(src_slide))
    set_notes(new, notes_text(src_slide))
    return new


# --------------------------------------------------------------------------
# Slides de DESIGN du template (slides d'exemple de 01. Template/*.potx)
# --------------------------------------------------------------------------
# Toute nouvelle slide part de la slide de design du template correspondant à son masque
# (et non du masque nu) : les éléments graphiques ajoutés dans les slides d'exemple du
# template (ex. cartes régions de « Nos bureaux ») sont ainsi repris automatiquement.
DESIGN_ALIASES = {"bureaux": "Disposition personnalisée"}   # alias lisibles -> nom de masque
_FR_MARKERS = re.compile(r"[éèêàùçœ]|\b(le|la|les|des|du|de|et|nos|vos|am[ée]rique|asie|suisse|nord)\b", re.I)


def _slide_texts(slide):
    out = []
    for sh, _, _ in iter_shapes(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip():
            out.append(sh.text_frame.text.strip())
    return out


def design_catalog(slides):
    """Catalogue des slides de design : [{n, slide, layout, lang, texts}] (n = n° dans le template).

    Quand plusieurs slides de design utilisent le même masque (ex. bureaux FR / EN), la langue
    est déduite du texte (la plus « française » -> "fr", les autres -> "en").
    """
    cat = []
    for n, s in enumerate(slides, 1):
        cat.append({"n": n, "slide": s, "layout": s.slide_layout.name.strip(), "lang": None,
                    "texts": _slide_texts(s)})
    by_layout = {}
    for d in cat:
        by_layout.setdefault(_exact(d["layout"]), []).append(d)
    for group in by_layout.values():
        if len(group) > 1:
            scores = [len(_FR_MARKERS.findall(" ".join(d["texts"]))) for d in group]
            if max(scores) > min(scores):          # vraie différence de langue
                best = scores.index(max(scores))
                for i, d in enumerate(group):
                    d["lang"] = "fr" if i == best else "en"
    return cat


def _exact(name):
    return re.sub(r"\s+", " ", (name or "").strip().lower())


def resolve_design(catalog, design=None, layout=None, lang="fr"):
    """Slide de design à utiliser.

    design : n° de slide du template (int), "Nom du masque", "Nom du masque|en" ou alias
             ("bureaux_fr", "bureaux_en"). layout : nom de masque (création standard).
    Renvoie None si le template n'a pas de slide de design pour ce masque.
    """
    if isinstance(design, int) or (isinstance(design, str) and design.isdigit()):
        return catalog[int(design) - 1]
    want_lang = lang
    target = layout
    if design:
        m = re.match(r"^(.*?)[_|](fr|en)$", design.strip(), re.I)
        base, lg = (m.group(1), m.group(2).lower()) if m else (design.strip(), None)
        target = DESIGN_ALIASES.get(base, base)
        want_lang = lg or lang
    cands = [d for d in catalog if _exact(d["layout"]) == _exact(target)] or         [d for d in catalog if _layout_key(d["layout"]) == _layout_key(target or "")]
    if not cands:
        if design:
            raise KeyError(f"Slide de design introuvable : {design!r} "
                           f"(designs : {[(d['n'], d['layout'], d['lang']) for d in catalog]})")
        return None
    for d in cands:
        if d["lang"] in (None, want_lang):
            return d
    return cands[0]


def reset_design(slide):
    """Vide une slide de design clonée : textes d'exemple des zones, zones orphelines
    (résidus sans masque), étiquettes d'exemple (ex. « Standard - Empty »)."""
    layout = slide.slide_layout
    layout_idx = {ph.placeholder_format.idx for ph in layout.placeholders}
    labels = {norm_label(layout.name), norm_label(_layout_key(layout.name))}
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx not in layout_idx:
            ph._element.getparent().remove(ph._element)
            continue
        if ph.has_text_frame:
            body = ph.text_frame._txBody
            paras = body.findall(A + "p")
            for p in paras[1:]:
                body.remove(p)
            for c in list(paras[0]):
                if c.tag in (A + "r", A + "br", A + "fld"):
                    paras[0].remove(c)
    for sh in list(slide.shapes):
        if not sh.is_placeholder and sh.has_text_frame and norm_label(sh.text_frame.text) in labels:
            sh._element.getparent().remove(sh._element)


def norm_label(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def new_slide(prs, catalog, layout_name=None, design=None, copier=None, keep_content=False, lang="fr"):
    """Nouvelle slide à partir de la slide de design du template (sinon du masque nu)."""
    d = resolve_design(catalog, design=design, layout=layout_name, lang=lang) if catalog else None
    if d is None:
        return prs.slides.add_slide(layout_by_name(prs, layout_name))
    slide = clone_slide(d["slide"], prs, copier)
    set_hidden(slide, False)
    if not keep_content:
        reset_design(slide)
    return slide


def delete_slide(prs, slide):
    """Supprime une slide (par OBJET, jamais par position)."""
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = sldId.get(R + "id")
        if prs.part.related_part(rId) is slide.part:
            prs.part.drop_rel(rId)
            sldIdLst.remove(sldId)
            return
    raise ValueError("slide introuvable")


def move_slide(prs, slide, new_index: int):
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        if prs.part.related_part(sldId.get(R + "id")) is slide.part:
            sldIdLst.remove(sldId)
            sldIdLst.insert(new_index, sldId)
            return


# --------------------------------------------------------------------------
# Transplant : importer des formes d'une slide source dans une zone de la slide cible
# --------------------------------------------------------------------------
def _xfrm(el):
    """Renvoie (off, ext) de l'élément de premier niveau (sp, pic, grpSp, graphicFrame, cxnSp)."""
    x = el.find(f".//{A}xfrm")
    if el.tag == P + "graphicFrame":
        x = el.find(P + "xfrm")
    elif el.tag == P + "grpSp":
        x = el.find(f"{P}grpSpPr/{A}xfrm")
    if x is None:
        return None
    off, ext = x.find(A + "off"), x.find(A + "ext")
    if off is None or ext is None:
        return None
    return x, off, ext


def transplant(src_slide, dst_slide, box, include=None, exclude=None, exclude_placeholders=True,
               copier: PartCopier | None = None, scale_fonts=True, allow_upscale=False,
               valign="center"):
    """Copie les formes de src_slide dans dst_slide, regroupées et mises à l'échelle dans box.

    box = (left, top, width, height) en pouces. include/exclude = noms de formes (niveau 1).
    Les proportions sont conservées ; le groupe est centré horizontalement dans la zone.
    """
    copier = copier or PartCopier(dst_slide.part.package)
    elems = []
    if include is not None:
        # noms, chemins "Groupe/Enfant", ou "Nom#2" (2e forme de ce nom) — ordre conservé
        for name in include:
            elems.append(find_shape(src_slide, name)._element)
    else:
        for sh in src_slide.shapes:
            if exclude and sh.name in exclude:
                continue
            if exclude_placeholders and sh.is_placeholder:
                continue
            elems.append(sh._element)
    if not elems:
        return None
    boxes = []
    for el in elems:
        t = _xfrm(el)
        if t:
            _, off, ext = t
            x, y, w, h = int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy"))
            boxes.append((x, y, x + w, y + h))
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    bw, bh = max(x1 - x0, 1), max(y1 - y0, 1)
    if box is None:  # position et taille d'origine conservées
        k, gw, gh, gx, gy = 1.0, bw, bh, x0, y0
    else:
        L, T, W, H = (int(Inches(v)) for v in box)
        k = min(W / bw, H / bh)
        if not allow_upscale:
            k = min(k, 1.0)
        gw, gh = int(bw * k), int(bh * k)
        gx = L + (W - gw) // 2
        gy = T if valign == "top" else T + (H - gh) // 2

    grp = etree.SubElement(dst_slide.shapes._spTree, P + "grpSp")
    ids = [int(e.get("id")) for e in dst_slide.shapes._spTree.iter(P + "cNvPr") if e.get("id", "").isdigit()]
    nv = etree.SubElement(grp, P + "nvGrpSpPr")
    etree.SubElement(nv, P + "cNvPr", id=str(max(ids + [1]) + 1), name="Transplant")
    etree.SubElement(nv, P + "cNvGrpSpPr")
    etree.SubElement(nv, P + "nvPr")
    gpr = etree.SubElement(grp, P + "grpSpPr")
    xf = etree.SubElement(gpr, A + "xfrm")
    etree.SubElement(xf, A + "off", x=str(gx), y=str(gy))
    etree.SubElement(xf, A + "ext", cx=str(gw), cy=str(gh))
    etree.SubElement(xf, A + "chOff", x=str(x0), y=str(y0))
    etree.SubElement(xf, A + "chExt", cx=str(bw), cy=str(bh))
    for el in elems:
        c = copy.deepcopy(el)
        # un placeholder transplanté devient une forme libre (sinon il hériterait du masque cible)
        for ph in c.iter(P + "ph"):
            ph.getparent().remove(ph)
        _ensure_geometry(c)
        grp.append(c)
        remap_element_rels(c, src_slide.part, dst_slide.part, copier)
    if scale_fonts and abs(k - 1) > 0.05:
        for tag in ("rPr", "defRPr", "endParaRPr"):
            for r in grp.iter(A + tag):
                if r.get("sz"):
                    r.set("sz", str(max(800, int(int(r.get("sz")) * k))))
    renumber_ids(dst_slide)
    return grp


def _ensure_geometry(el):
    """Une zone (placeholder) transplantée n'hérite plus de la forme de son masque : sans
    géométrie propre, PowerPoint ne l'affiche pas (ex. image de schéma) -> rectangle par défaut."""
    for sp in [el] + list(el.iter(P + "sp", P + "pic")):
        sppr = sp.find(P + "spPr")
        if sppr is None or sppr.find(A + "xfrm") is None:
            continue
        if sppr.find(A + "prstGeom") is None and sppr.find(A + "custGeom") is None:
            geom = etree.Element(A + "prstGeom", prst="rect")
            etree.SubElement(geom, A + "avLst")
            sppr.find(A + "xfrm").addnext(geom)


def renumber_ids(slide):
    """Garantit des id de formes uniques après import."""
    n = 1
    for c in slide.shapes._spTree.iter(P + "cNvPr"):
        n += 1
        c.set("id", str(n))


# --------------------------------------------------------------------------
# Remplissage des zones (placeholders)
# --------------------------------------------------------------------------
def fill_placeholder(ph, value):
    """value : str | [str | {"text":..., "level":n, "bold":bool}]"""
    tf = ph.text_frame
    items = value if isinstance(value, list) else [value]
    # conserve la mise en forme de la 1re ligne héritée du masque
    first = True
    for it in items:
        if isinstance(it, dict):
            text, level, bold = it.get("text", ""), it.get("level", 0), it.get("bold")
        else:
            text, level, bold = str(it), 0, None
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        if first:
            for r in list(para.runs):
                r._r.getparent().remove(r._r)
        first = False
        para.level = level
        lines = text.split("\n")
        for li, line in enumerate(lines):
            run = para.add_run()
            run.text = line
            if bold is not None:
                run.font.bold = bold
            if li < len(lines) - 1:
                run._r.addnext(etree.Element(A + "br"))
    return ph


def placeholder(slide, idx):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    raise KeyError(f"Zone idx={idx} absente du masque {slide.slide_layout.name!r} "
                   f"(zones : {[p.placeholder_format.idx for p in slide.placeholders]})")


def remove_empty_placeholders(slide, keep=(0,)):
    for ph in list(slide.placeholders):
        idx = ph.placeholder_format.idx
        if idx in keep:
            continue
        if ph.has_text_frame and not ph.text_frame.text.strip():
            ph._element.getparent().remove(ph._element)


def set_geometry(shape, left=None, top=None, width=None, height=None):
    if left is not None: shape.left = Inches(left)
    if top is not None: shape.top = Inches(top)
    if width is not None: shape.width = Inches(width)
    if height is not None: shape.height = Inches(height)


# --------------------------------------------------------------------------
# Copie de texte avec sa mise en forme "de contenu" (gras, surlignage, numérotation)
# --------------------------------------------------------------------------
KEEP_RPR_ATTRS = {"lang", "b", "i", "u", "strike", "cap", "dirty"}
KEEP_RPR_CHILDREN = {A + "highlight", A + "hlinkClick"}


def _clean_run_props(rpr):
    for k in list(rpr.attrib):
        if k not in KEEP_RPR_ATTRS:
            del rpr.attrib[k]
    for c in list(rpr):
        if c.tag not in KEEP_RPR_CHILDREN:
            rpr.remove(c)


WHITE_VALUES = {"FFFFFF", "bg1", "lt1"}


def _keep_text_color(rpr_src, rpr_dst):
    """Recopie la couleur de texte d'origine (mise en valeur) sauf le blanc (illisible sur fond blanc)."""
    sf = rpr_src.find(A + "solidFill")
    if sf is None or not len(sf):
        return
    clr = sf[0]
    if clr.get("val", "").upper() in WHITE_VALUES or clr.get("val") in WHITE_VALUES:
        return
    rpr_dst.insert(0, copy.deepcopy(sf))


def copy_paragraphs(src_shape, ph, src_part=None, dst_part=None, copier=None, keep_color=False):
    """Remplace le texte de la zone `ph` par les paragraphes de `src_shape` (verbatim).

    Conservés : texte, retours à la ligne, niveaux, numérotation auto, gras/italique/souligné,
    surlignage (+ couleurs de mise en valeur si keep_color). Supprimés : tailles, polices,
    couleurs (=> style du masque / charte ; recharte passe ensuite les anciens violets au rouge charte).
    """
    body = ph.text_frame._txBody
    for p in body.findall(A + "p"):
        body.remove(p)
    for p in src_shape.text_frame._txBody.findall(A + "p"):
        c = copy.deepcopy(p)
        ppr = c.find(A + "pPr")
        if ppr is not None:
            for k in list(ppr.attrib):
                if k != "lvl":
                    del ppr.attrib[k]
            for ch in list(ppr):
                if ch.tag != A + "buAutoNum":
                    ppr.remove(ch)
        originals = [copy.deepcopy(r) for r in c.iter(A + "rPr")] if keep_color else []
        for tag in ("rPr", "endParaRPr"):
            for rpr in c.iter(A + tag):
                _clean_run_props(rpr)
        if keep_color:
            for orig, rpr in zip(originals, list(c.iter(A + "rPr"))):
                _keep_text_color(orig, rpr)
        body.append(c)
        if src_part is not None:
            remap_element_rels(c, src_part, dst_part, copier)
    return ph


def set_gradient_background(slide):
    csld = slide._element.find(P + "cSld")
    old = csld.find(P + "bg")
    if old is not None:
        csld.remove(old)
    bg = etree.Element(P + "bg")
    csld.insert(0, bg)
    bgpr = etree.SubElement(bg, P + "bgPr")
    bgpr.append(charte_gradient())
    etree.SubElement(bgpr, A + "effectLst")


def recolor_svg_icons(slide):
    """Icônes SVG : anciens violets -> CD5358 (le PNG de repli n'est pas modifié)."""
    done = []
    for rel in slide.part.rels.values():
        if rel.is_external or getattr(rel.target_part, "content_type", "") != "image/svg+xml":
            continue
        part = rel.target_part
        blob = part.blob
        new = blob
        for v in OLD_VIOLETS:
            new = re.sub(("#" + v).encode(), ("#" + RED2).encode(), new, flags=re.I)
        if new != blob:
            part._blob = new
            done.append(str(part.partname))
    return done


def find_shape(slide, name):
    """Forme par nom, chemin "Groupe/Enfant" ou "Nom#n" (n-ième forme portant ce nom)."""
    base, _, nth = name.partition("#")
    nth = int(nth) if nth.isdigit() else 1
    hits = [sh for sh, _, path in iter_shapes(slide.shapes) if base in (path, sh.name)]
    if len(hits) < nth:
        raise KeyError(f"forme source introuvable : {name!r}")
    return hits[nth - 1]


SVG_BLIP = "{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip"


def recolor_icons(root_el, slide, color, copier):
    """Recolore des icônes (SVG et formes vectorielles) dans la couleur charte donnée.

    SVG : copie de l'image (les autres usages ne sont pas modifiés), toutes les couleurs de
    remplissage/trait remplacées. Formes : remplissages et traits passés en `color`.
    """
    for blip in root_el.iter(SVG_BLIP):
        rid = blip.get(R + "embed")
        part = slide.part.related_part(rid)
        blob = re.sub(rb'(fill|stroke)(=")#[0-9A-Fa-f]{3,6}"',
                      lambda m: m.group(1) + m.group(2) + b"#" + color.encode() + b'"', part.blob)
        blob = re.sub(rb'(fill|stroke):\s*#[0-9A-Fa-f]{3,6}',
                      lambda m: m.group(1) + b":#" + color.encode(), blob)
        # classes "MsftOfcThm_*" : PowerPoint réapplique la couleur du thème au rendu -> neutraliser
        blob = blob.replace(b"MsftOfcThm_", b"CaptiveaIcon_")
        if b"fill" not in blob[:5000] and b"<path" in blob:
            blob = blob.replace(b"<path", b'<path fill="#' + color.encode() + b'"')
        new = Part(copier._next_partname("/ppt/media/image.svg"), "image/svg+xml", slide.part.package, blob)
        blip.set(R + "embed", slide.part.relate_to(new, RT.IMAGE))
    for tag in ("spPr", "grpSpPr"):
        for sppr in root_el.iter(P + tag):
            for holder in [sppr] + sppr.findall(A + "ln"):
                sf = holder.find(A + "solidFill")
                if sf is not None:
                    for c in list(sf):
                        sf.remove(c)
                    etree.SubElement(sf, A + "srgbClr", val=color)


def set_font_size(ph, pt):
    """Impose une taille de police (pt) à tout le texte d'une zone."""
    for p in ph.text_frame._txBody.findall(A + "p"):
        runs = p.findall(A + "r")
        for r in runs:
            rpr = r.find(A + "rPr")
            if rpr is None:
                rpr = etree.Element(A + "rPr")
                r.insert(0, rpr)
            rpr.set("sz", str(int(pt * 100)))
        end = p.find(A + "endParaRPr")
        if end is not None:
            end.set("sz", str(int(pt * 100)))


def tighten(ph):
    """Supprime l'espace avant/après les paragraphes d'une zone (texte dense)."""
    for p in ph.text_frame._txBody.findall(A + "p"):
        ppr = p.find(A + "pPr")
        if ppr is None:
            ppr = etree.Element(A + "pPr")
            p.insert(0, ppr)
        for tag in ("lnSpc", "spcBef", "spcAft"):
            old = ppr.find(A + tag)
            if old is not None:
                ppr.remove(old)
        order = []
        for tag, val in (("lnSpc", ("spcPct", "100000")), ("spcBef", ("spcPts", "0")), ("spcAft", ("spcPts", "0"))):
            el = etree.Element(A + tag)
            etree.SubElement(el, A + val[0], val=val[1])
            order.append(el)
        for el in reversed(order):
            ppr.insert(0, el)


# --------------------------------------------------------------------------
# Fiches "fonctionnalités" : titre de fonctionnalité + description, en colonnes
# --------------------------------------------------------------------------
def _clean_para(p, level=0):
    c = copy.deepcopy(p)
    ppr = c.find(A + "pPr")
    if ppr is not None:
        c.remove(ppr)
    ppr = etree.Element(A + "pPr")
    if level:
        ppr.set("lvl", str(level))
    c.insert(0, ppr)
    for tag in ("rPr", "endParaRPr"):
        for rpr in c.iter(A + tag):
            _clean_run_props(rpr)
    return c, ppr


def _style_runs(p, size=None, bold=None, color=None):
    for r in p.findall(A + "r"):
        rpr = r.find(A + "rPr")
        if rpr is None:
            rpr = etree.Element(A + "rPr")
            r.insert(0, rpr)
        if size:
            rpr.set("sz", str(int(size * 100)))
        if bold is not None:
            rpr.set("b", "1" if bold else "0")
        if color:
            for c in list(rpr):
                if c.tag in (A + "solidFill", A + "gradFill"):
                    rpr.remove(c)
            sf = etree.Element(A + "solidFill")
            etree.SubElement(sf, A + "srgbClr", val=color)
            rpr.insert(0, sf)


def fill_features(ph, groups, src_slide, heading_size=13, text_size=10.5, color="BA131A"):
    """groups = [[titre, description, ...], ...] (noms de formes source).

    Titre : gras, rouge charte, sans puce. Descriptions : puces du masque, verbatim.
    """
    body = ph.text_frame._txBody
    for p in body.findall(A + "p"):
        body.remove(p)
    first = True
    for grp in groups:
        for k, name in enumerate(grp):
            if name is None:      # bloc de description sans titre de fonctionnalité
                continue
            shp = find_shape(src_slide, name)
            paras = [p for p in shp.text_frame._txBody.findall(A + "p")
                     if "".join(t.text or "" for t in p.iter(A + "t")).strip()]
            for p in paras:
                c, ppr = _clean_para(p)
                if k == 0:
                    etree.SubElement(ppr, A + "buNone")
                    ppr.set("marL", "0")
                    ppr.set("indent", "0")
                    sb = etree.Element(A + "spcBef")
                    etree.SubElement(sb, A + "spcPts", val="0" if first else "900")
                    ppr.insert(0, sb)
                    _style_runs(c, heading_size, True, color)
                else:
                    sb = etree.Element(A + "spcBef")
                    etree.SubElement(sb, A + "spcPts", val="200")
                    ppr.insert(0, sb)
                    _style_runs(c, text_size, None, None)
                body.append(c)
                first = False
    return ph


def fix_picture_aspect(slide, tolerance=0.03):
    """Rétablit les proportions des images déformées (réduit une dimension, centre conservé)."""
    fixed = []
    for sh, _, path in iter_shapes(slide.shapes):
        if sh._element.tag != P + "pic":
            continue
        try:
            pw, phh = sh.image.size
        except Exception:
            continue
        cw = 1 - (sh.crop_left + sh.crop_right)
        ch = 1 - (sh.crop_top + sh.crop_bottom)
        if not (pw and phh and sh.width and sh.height and ch > 0):
            continue
        img_r = (pw * cw) / (phh * ch)
        box_r = sh.width / sh.height
        if abs(img_r / box_r - 1) <= tolerance:
            continue
        xfrm = sh._element.find(f".//{A}xfrm")
        off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
        x, y, w, h = (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
        if box_r > img_r:          # trop large -> réduire la largeur
            nw = int(h * img_r); off.set("x", str(x + (w - nw) // 2)); ext.set("cx", str(nw))
        else:                      # trop haute -> réduire la hauteur
            nh = int(w / img_r); off.set("y", str(y + (h - nh) // 2)); ext.set("cy", str(nh))
        fixed.append(path)
    return fixed


def make_badge(root_el):
    """Pastille ronde au dégradé charte pour une zone de texte posée (le cercle d'origine était
    porté par l'ancien masque : sans lui, un texte blanc devient invisible sur fond blanc)."""
    for sp in root_el.iter(P + "sp"):
        sppr = sp.find(P + "spPr")
        if sppr is None:
            continue
        geom = sppr.find(A + "prstGeom")
        if geom is not None:
            geom.set("prst", "ellipse")
        for f in list(sppr):
            if f.tag in (A + "noFill", A + "solidFill", A + "gradFill"):
                sppr.remove(f)
        anchor = geom if geom is not None else sppr.find(A + "xfrm")
        anchor.addnext(charte_gradient())
