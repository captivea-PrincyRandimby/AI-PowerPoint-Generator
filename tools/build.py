"""Construction d'un PPT à la nouvelle charte à partir d'un PLAN JSON.

  python tools/build.py init "<source 02>"     -> crée work/<doc>/plan.json (squelette à compléter)
  python tools/build.py run  "<plan.json>"     -> construit le .pptx dans 04 (miroir), recharte,
                                                  écrit work/<doc>/build_log.json
Options run : --out <chemin>     (sortie alternative, ex. version de test ; obligatoire hors dossiers 02-05)
              --source <chemin>  (remplace la source du plan, ex. fichier joint dans claude.ai)

Toute nouvelle slide part de la SLIDE DE DESIGN du template (01. Template/*.potx) qui utilise le
masque demandé : on clone la slide d'exemple du template (design complet), on la vide de ses
textes d'exemple puis on la remplit. À défaut de slide de design, le masque nu est utilisé.
Catalogue : tools/catalog/layouts.md (masques + slides de design) · python tools/layouts.py

---------------------------------------------------------------------------
FORMAT DU PLAN
{
  "source": "02. French PPT to transform/…/FR - X.potx",
  "output": "04. Render from claude/…/FR - X.pptx",          (défaut : miroir de la source)
  "lang": "fr" | "en"                                         (défaut : déduit du nom de sortie)
  "slides": [ {…}, {…} ]                                      (dans l'ordre de SORTIE)
}
Chaque slide :
  "src": 12                 n° de slide source (notes + état masqué repris automatiquement)
  "mode":
     "fill"       slide de design du masque + zones remplies (cas par défaut)
     "transplant" idem + formes source importées, mises à l'échelle dans "box"
     "design"     slide de design du template reprise AVEC son contenu : "design": "bureaux_fr",
                  "bureaux_en", "Nom du masque", "Nom du masque|en" ou n° de slide du template
     "reuse"      copie telle quelle d'une slide validée : "from": "<pptx>", "slide": n
     "clone"      copie brute de la slide source (exception, puis recharte), posée sur le masque du
                  même nom du template ; "zones" y corrige une zone précise (ex. capsule).
                  Cas normal : source déjà à la charte 2026 (version validée 05 d'un ancien template)
     "summary"    sommaire généré depuis les slides marquées "section"
  "layout": "Boxed - 3 columns"           nom exact du masque (voir tools/catalog/layouts.md)
  "zones": {"0": "Titre", "13": "CAPSULE", "15": ["puce 1", {"text": "sous-puce", "level": 1}]}
           Conventions du template : couverture « 1_Main Title » = titre 0 + sous-titre 1 ;
           « Section Title » = titre 0, capsule 13, numéro de section dans la zone 1.
  "section": {"num": "01", "label": "Captivea et Odoo"}   marque une slide de section (sommaire)
  "box": [left, top, width, height]       (transplant) zone cible en pouces
  "include": [noms] / "exclude": [noms]   (transplant) formes source retenues / écartées
  "upscale": true                         (transplant) autoriser l'agrandissement (défaut : non)
  "valign": "center"|"top"                (transplant) alignement vertical dans la zone
  "absolute": true                        (transplant) positions et tailles d'origine conservées
  "geometry": {"15": [l, t, w, h]}        redimensionner / déplacer une zone
  "keep_empty": [idx]                     zones vides à conserver (sinon supprimées)
  "copy_text": {"2": "Nom forme source"}  copie verbatim d'un texte source dans une zone
                                          (garde gras / surlignage / numérotation, style du masque)
  "keep_color": [idx]                     (copy_text) garde aussi les couleurs de mise en valeur
                                          (sauf blanc ; anciens violets -> rouge charte)
  "place": [{"shapes": ["Graphic 4" | "Groupe 30/Graphique 15"], "box": [l,t,w,h]}]
                                          pose des formes source précises dans une zone (icônes 5c…)
                                          + "recolor": "BA131A" pour recolorer l'icône à la charte
                                          + "badge": true : pastille ronde au dégradé charte (chiffre clé
                                            dont le cercle d'origine venait de l'ancien masque)
  Noms de formes : nom, chemin "Groupe/Enfant", ou "Nom#2" pour la 2e forme portant ce nom
  "features": {"1": [["Titre fct", "Description fct"], ...]}   fiches fonctionnalités :
                                          titre rouge gras sans puce + description à puces (verbatim)
  "heading_size" / "text_size": 13 / 10.5 tailles (pt) des fiches fonctionnalités
  "background": "gradient"                fond de slide = dégradé charte
  "font_size": {"16": 11}                 taille (pt) imposée au texte d'une zone (débordements)
  "anchor_top": [idx]                     texte ancré en haut de la zone
  "tight": [idx]                          espacement entre paragraphes réduit (texte dense)
  "recolor": {"color": "BA131A", "shapes": [noms]}  recolore des icônes transplantées (blanches…)
  Astuce : cercle à garder sans numéro visible -> valeur "​" (caractère invisible)
  "hidden": true|false                    force l'état masqué (défaut : celui de la source)
  "notes": "…"                            force les notes (défaut : notes de la source)
  "method": "5a"|"5b"|"5c"|"5d"|"texte"   traitement retenu (traçabilité / audit)
  "comment": "…"                          justification libre (non publiée)
---------------------------------------------------------------------------
"""
import argparse
import json
import re
import sys
from pathlib import Path

from common import (A, ROOT, RENDER, TEMPLATE, is_hidden, iter_shapes, norm, notes_text,
                    open_prs, rel_or_abs, rel_to_source_root, safe_output, set_hidden, set_notes, work_dir)
from pptxops import (PartCopier, clone_slide, copy_paragraphs, delete_slide, design_catalog,
                     fill_features, fill_placeholder, find_shape, fix_picture_aspect, make_badge, new_slide,
                     placeholder, recolor_icons, recolor_svg_icons, remove_empty_placeholders,
                     set_font_size, set_geometry, set_gradient_background, tighten, transplant)
from recharte import recharte_prs

SUMMARY_NUM = [14, 18, 22, 26, 30, 16, 20, 24, 28, 32]   # colonne gauche puis droite
OFFICES_TITLES = re.compile(r"^(nos bureaux|our offices)$", re.I)


def resolve(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def default_output(source: Path) -> Path:
    rel = rel_to_source_root(source)
    return RENDER / rel.parent / (rel.stem + ".pptx")


def doc_lang(output: Path, plan: dict) -> str:
    if plan.get("lang") in ("fr", "en"):
        return plan["lang"]
    return "en" if re.match(r"^(EN|US)\b", Path(output).stem, re.I) else "fr"


# --------------------------------------------------------------------------
def cmd_init(source: Path):
    source = source.resolve()
    inv_path = work_dir(source) / "inventory.json"
    if not inv_path.exists():
        sys.exit(f"Lancer d'abord : python tools/inventory.py \"{source}\"")
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    plan_path = work_dir(source) / "plan.json"
    if plan_path.exists():
        sys.exit(f"Plan déjà existant (non écrasé) : {plan_path}")
    en = source.stem.upper().startswith(("EN", "US"))
    first = inv["slides"][0]
    slides = [{"mode": "fill", "layout": "1_Main Title", "src": 1, "method": "couverture",
               "zones": {"0": first["title"] or "", "1": ""}},
              {"mode": "summary", "layout": "Summary",
               "zones": {"0": "TABLE OF CONTENTS" if en else "SOMMAIRE",
                         "13": "TABLE OF CONTENTS" if en else "SOMMAIRE"},
               "comment": "convention validée : même libellé en titre et en capsule"}]
    n_section = 0
    for s in inv["slides"][1:]:
        title = s["title"] or ""
        paras = [norm(p) for t in s["texts"] for p in t.get("paragraphs", [])]
        if any(OFFICES_TITLES.match(p) for p in paras):
            slides.append({"src": s["n"], "mode": "design", "design": "bureaux_en" if en else "bureaux_fr",
                           "method": "slide de design du template (bureaux)", "hidden": s["hidden"]})
            continue
        if "SECTION probable" in s["hints"]:
            n_section += 1
            num = f"{n_section:02d}"
            slides.append({"src": s["n"], "mode": "fill", "layout": "Section Title", "method": "section",
                           "zones": {"0": title, "1": num, "13": "TODO capsule"},
                           "section": {"num": num, "label": title.capitalize()}, "hidden": s["hidden"],
                           "comment": "section probable à confirmer · " + " · ".join(s["hints"])})
            continue
        slides.append({"src": s["n"], "mode": "TODO", "layout": "TODO", "method": "TODO",
                       "zones": {"0": title, "13": "TODO capsule"},
                       "hidden": s["hidden"], "comment": " · ".join(s["hints"])})
    plan = {"source": rel_or_abs(source), "lang": "en" if en else "fr", "slides": slides}
    try:
        plan["output"] = rel_or_abs(default_output(source))
    except ValueError:              # fichier hors 02-05 : sortie à préciser avec --out
        pass
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Squelette -> {plan_path}")


# --------------------------------------------------------------------------
def build_slide(prs, spec, src_prs, copier, sections, reuse_cache, catalog, lang):
    mode = spec.get("mode", "fill")
    src = src_prs.slides[spec["src"] - 1] if spec.get("src") else None

    if mode == "reuse":
        fpath = resolve(spec["from"])
        key = str(fpath)
        if key not in reuse_cache:
            reuse_cache[key] = (open_prs(fpath), PartCopier(prs.part.package))
        rprs, rcop = reuse_cache[key]
        slide = clone_slide(rprs.slides[spec.get("slide", 1) - 1], prs, rcop)
        if src is not None and "notes" not in spec and notes_text(src):
            set_notes(slide, notes_text(src))   # les notes du document traité priment
    elif mode == "clone":
        slide = clone_slide(src, prs, copier, layout_name=spec.get("layout"))
        for k, v in spec.get("zones", {}).items():      # correction ponctuelle (ex. capsule)
            ph = placeholder(slide, int(k))
            ph.text_frame.clear()
            fill_placeholder(ph, v)
    else:
        if mode == "design":
            slide = new_slide(prs, catalog, design=spec["design"], copier=copier,
                              keep_content=True, lang=lang)
        else:
            slide = new_slide(prs, catalog, layout_name=spec["layout"], copier=copier, lang=lang)
        zones = dict(spec.get("zones", {}))
        if mode == "summary":
            items = sections
            if len(items) > len(SUMMARY_NUM):
                raise ValueError(f"{len(items)} sections > 10 cases du sommaire")
            for (num, label), idx in zip(items, SUMMARY_NUM):
                zones.setdefault(str(idx), num)
                zones.setdefault(str(idx + 1), label)
        for k, v in zones.items():
            if v in ("", None) or (isinstance(v, str) and v.startswith("TODO")):
                continue
            fill_placeholder(placeholder(slide, int(k)), v)
        keep_color = {int(i) for i in spec.get("keep_color", [])}
        for k, name in spec.get("copy_text", {}).items():
            copy_paragraphs(find_shape(src, name), placeholder(slide, int(k)),
                            src.part, slide.part, copier, keep_color=int(k) in keep_color)
        for k, groups in spec.get("features", {}).items():
            fill_features(placeholder(slide, int(k)), groups, src,
                          spec.get("heading_size", 13), spec.get("text_size", 10.5))
        for k, g in spec.get("geometry", {}).items():
            set_geometry(placeholder(slide, int(k)), *g)
        if mode == "transplant":
            if src is None:
                raise ValueError("transplant sans 'src'")
            box = None if spec.get("absolute") else spec.get("box", [0.76, 2.55, 11.81, 4.3])
            transplant(src, slide, box,
                       include=spec.get("include"), exclude=spec.get("exclude"), copier=copier,
                       allow_upscale=spec.get("upscale", False),
                       valign=spec.get("valign", "center"))
        for pl in spec.get("place", []):
            grp = transplant(src, slide, pl["box"], include=pl["shapes"], copier=copier,
                             allow_upscale=pl.get("upscale", True), valign=pl.get("valign", "center"),
                             scale_fonts=pl.get("scale_fonts", True))
            if pl.get("recolor"):
                recolor_icons(grp, slide, pl["recolor"], copier)
            if pl.get("badge"):
                make_badge(grp)
        rc = spec.get("recolor")
        if rc:
            names = set(rc["shapes"])
            for sh, _, path in iter_shapes(slide.shapes):
                if sh.name in names:
                    recolor_icons(sh._element, slide, rc["color"], copier)
        for k, pt in spec.get("font_size", {}).items():
            set_font_size(placeholder(slide, int(k)), pt)
        for k in spec.get("tight", []):
            tighten(placeholder(slide, int(k)))
        for k in spec.get("anchor_top", []):
            placeholder(slide, int(k)).text_frame._txBody.find(A + "bodyPr").set("anchor", "t")
        if spec.get("background") == "gradient":
            set_gradient_background(slide)
        remove_empty_placeholders(slide, keep=[0] + [int(i) for i in spec.get("keep_empty", [])])

    hidden = spec.get("hidden", is_hidden(src) if src is not None else None)
    if hidden is not None:
        set_hidden(slide, hidden)
    if "notes" in spec:
        set_notes(slide, spec["notes"])
    elif src is not None and mode != "clone" and not notes_text(slide):
        set_notes(slide, notes_text(src))
    return slide


def cmd_run(plan_path: Path, out=None, source_override=None):
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    todo = [i for i, s in enumerate(plan["slides"], 1)
            if "TODO" in json.dumps({k: v for k, v in s.items() if k != "comment"})]
    if todo:
        sys.exit(f"Plan incomplet : entrées {todo} contiennent encore TODO")
    source = resolve(source_override or plan["source"])
    if out or plan.get("output"):
        output = resolve(out or plan["output"])
    else:
        try:
            output = default_output(source)
        except ValueError:
            sys.exit("Source hors des dossiers 02-05 : préciser la sortie avec --out")
    safe_output(output)
    lang = doc_lang(output, plan)
    src_prs = open_prs(source)
    prs = open_prs(TEMPLATE)
    template_slides = list(prs.slides)          # slides de design : supprimées APRÈS ajout
    catalog = design_catalog(template_slides)
    copier = PartCopier(prs.part.package)
    sections = [(s["section"]["num"], s["section"]["label"]) for s in plan["slides"] if s.get("section")]
    reuse_cache, log = {}, []
    for i, spec in enumerate(plan["slides"], 1):
        try:
            build_slide(prs, spec, src_prs, copier, sections, reuse_cache, catalog, lang)
        except Exception as e:
            sys.exit(f"Erreur entrée {i} (src={spec.get('src')}, layout={spec.get('layout')}) : {e}")
        log.append({"out": i, "src": spec.get("src"), "mode": spec.get("mode", "fill"),
                    "layout": spec.get("layout"), "design": spec.get("design"),
                    "method": spec.get("method"), "section": spec.get("section"),
                    "from": spec.get("from")})
    for s in template_slides:
        delete_slide(prs, s)
    rep = recharte_prs(prs)
    for i, sl in enumerate(prs.slides, 1):
        rep += [f"slide {i}: icône SVG recolorée {p}" for p in recolor_svg_icons(sl)]
        rep += [f"slide {i}: proportions d'image rétablies {p}" for p in fix_picture_aspect(sl)]
    prs.save(str(output))
    wd = work_dir(source)
    (wd / "build_log.json").write_text(json.dumps(
        {"source": str(source), "output": str(output), "template": str(TEMPLATE), "lang": lang,
         "slides": log, "recharte": rep}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(log)} slides -> {output}")
    print(f"Recharte : {len(rep)} corrections (détail dans build_log.json)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "run"])
    ap.add_argument("path")
    ap.add_argument("--out")
    ap.add_argument("--source")
    a = ap.parse_args()
    if a.cmd == "init":
        cmd_init(Path(a.path))
    else:
        cmd_run(Path(a.path).resolve(), a.out, a.source and Path(a.source).resolve())


if __name__ == "__main__":
    main()
