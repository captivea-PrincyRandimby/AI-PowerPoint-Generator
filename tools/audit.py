"""Audit QA d'un rendu (gate avant livraison).

  python tools/audit.py "<rendu .pptx>"                 (mode FR : utilise work/<doc>/build_log.json)
  python tools/audit.py "<rendu EN .pptx>" --en "<FR validé .pptx>"   (mode traduction)
  python tools/audit.py "<pptx>" --standalone           (contrôles charte seuls, ex. un fichier 05)

Sortie : work/<doc>/audit.md ; code retour 1 si au moins une ERREUR (bloquante).
"""
import argparse
import json
import re
import unicodedata
import sys
from pathlib import Path

from common import (A, ALLOWED_FONTS, CHARTE_COLORS, OLD_VIOLETS, P, RED, TEMPLATE,
                    WORK, is_hidden, is_picture, iter_shapes, norm, notes_text, open_prs,
                    shape_texts, work_dir)
from inventory import ILLUSTRATION_MARKERS
from recharte import MIN_BG_AREA_IN2, _area_in2, _is_charte_gradient, _is_red

FR_WORDS = re.compile(r"\b(les|des|une|nous|vous|avec|pour|dans|sur|est|sont|votre|vos|notre|nos|"
                      r"projet|équipe|être|également|déjà|à|où|après|très)\b", re.I)


class Report:
    def __init__(self):
        self.errors, self.warnings, self.ok = [], [], []

    def err(self, where, msg): self.errors.append(f"**{where}** — {msg}")
    def warn(self, where, msg): self.warnings.append(f"{where} — {msg}")

    def md(self, title):
        out = [f"# Audit — {title}", "",
               f"**{len(self.errors)} erreur(s) bloquante(s) · {len(self.warnings)} avertissement(s)**", ""]
        if self.errors:
            out += ["## ❌ Erreurs (à corriger avant livraison)", ""] + [f"- {e}" for e in self.errors] + [""]
        if self.warnings:
            out += ["## ⚠ Avertissements (à vérifier visuellement)", ""] + [f"- {w}" for w in self.warnings] + [""]
        if self.ok:
            out += ["## ✅ Contrôles passés", ""] + [f"- {o}" for o in self.ok]
        return "\n".join(out)


def template_samples(tpl):
    """Textes d'exemple du template (titres des slides de design, noms de masques)."""
    out = {norm(l.name).lower() for l in tpl.slide_layouts}
    for s in tpl.slides:
        for ph in s.placeholders:
            if ph.has_text_frame and norm(ph.text_frame.text):
                out.add(norm(ph.text_frame.text).lower())
    return out


def charte_checks(prs, rep):
    from pptxops import _layout_key
    tpl = open_prs(TEMPLATE)
    tpl_layouts = {_layout_key(l.name) for l in tpl.slide_layouts}
    samples = template_samples(tpl)
    bad_layouts, n_sections, summary = [], 0, None
    for i, s in enumerate(prs.slides, 1):
        w = f"Slide {i}"
        el = s._element
        lname = s.slide_layout.name.strip()
        if _layout_key(lname) not in tpl_layouts:
            bad_layouts.append(i)
            rep.err(w, f"masque hors template : {lname!r}")
        if lname == "Section Title":
            n_sections += 1
        if lname == "Summary":
            summary = i
        fonts = {f.get("typeface") for t in ("latin", "ea", "cs") for f in el.iter(A + t)} - {None, ""}
        bad = sorted(fonts - ALLOWED_FONTS)
        if bad:
            rep.err(w, f"polices hors charte : {bad}")
        if any(c.get("val") == "accent6" for c in el.iter(A + "schemeClr")):
            rep.err(w, "couleur de thème accent6 (= ancien violet 714B67 dans le thème du template)")
        colors = {c.get("val", "").upper() for c in el.iter(A + "srgbClr")}
        if colors & OLD_VIOLETS:
            rep.err(w, f"anciens violets : {sorted(colors & OLD_VIOLETS)}")
        other = sorted(colors - CHARTE_COLORS - OLD_VIOLETS)
        if other:
            rep.warn(w, f"couleurs hors palette : {other[:8]}")
        for tag in (P + "spPr", P + "bgPr", P + "grpSpPr"):
            for sppr in el.iter(tag):
                area = 999 if tag == P + "bgPr" else _area_in2(sppr)
                for fill in sppr:
                    if fill.tag == A + "solidFill" and _is_red(fill) and (area is None or area >= MIN_BG_AREA_IN2):
                        rep.err(w, f"aplat #{RED} en fond (≈{area and round(area,1)} in²)")
                    if fill.tag == A + "gradFill" and not _is_charte_gradient(fill):
                        rep.err(w, "ancien dégradé")
        # images
        for sh, depth, path in iter_shapes(s.shapes):
            if is_picture(sh):
                try:
                    blob = sh.image.blob
                    if ILLUSTRATION_MARKERS.search(blob[:200000]) and sh.image.ext in ("svg", "emf", "wmf"):
                        rep.err(w, f"illustration Freepik/amico : {path}")
                    px_w, px_h = sh.image.size
                    crop_w = 1 - (sh.crop_left + sh.crop_right)
                    crop_h = 1 - (sh.crop_top + sh.crop_bottom)
                    if px_w and px_h and sh.height and crop_h > 0:
                        img_r = (px_w * crop_w) / (px_h * crop_h)
                        box_r = sh.width / sh.height
                        if abs(img_r / box_r - 1) > 0.04:
                            rep.err(w, f"image déformée : {path} (ratio {box_r:.2f} vs {img_r:.2f})")
                except Exception:
                    pass
            if depth == 0 and sh.left is not None and sh.width is not None:
                if sh.left < -10000 or sh.top < -10000 or sh.left + sh.width > prs.slide_width + 10000 \
                        or sh.top + sh.height > prs.slide_height + 10000:
                    rep.warn(w, f"forme hors slide : {path}")
        # texte d'exemple du template resté en place (slide de design non remplie)
        for ph in s.placeholders:
            if ph.has_text_frame and norm(ph.text_frame.text).lower() in samples:
                rep.err(w, f"texte d'exemple du template non remplacé : {norm(ph.text_frame.text)!r}")
        # zones vides (texte d'invite visible en édition)
        for ph in s.placeholders:
            if ph.has_text_frame and not ph.text_frame.text.strip() and ph.placeholder_format.idx != 0:
                rep.warn(w, f"zone vide conservée idx={ph.placeholder_format.idx}")
        # titre = capsule
        try:
            t = norm(next(p for p in s.placeholders if p.placeholder_format.idx == 0).text_frame.text)
            c = norm(next(p for p in s.placeholders if p.placeholder_format.idx == 13).text_frame.text)
            if t and c and t.lower() == c.lower() and _layout_key(lname) != "summary":
                rep.err(w, f"titre identique à la capsule : {t!r}")
        except StopIteration:
            pass
    if not bad_layouts:
        rep.ok.append("tous les masques proviennent du template")
    if n_sections and not summary:
        rep.err("Document", f"{n_sections} sections mais AUCUN sommaire")
    elif summary:
        rep.ok.append(f"sommaire présent (slide {summary}), {n_sections} sections")
    if summary and summary != 2:
        rep.warn("Document", f"sommaire en position {summary} (attendu : juste après la couverture)")


def unaccent(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def fr_checks(prs, log, rep):
    src = open_prs(Path(log["source"]))
    covered = set()
    for entry in log["slides"]:
        if not entry.get("src"):
            continue
        n_out, n_src = entry["out"], entry["src"]
        covered.add(n_src)
        so, ss = prs.slides[n_out - 1], src.slides[n_src - 1]
        w = f"Slide {n_out} (source {n_src})"
        if is_hidden(so) != is_hidden(ss):
            rep.err(w, f"état masqué différent (source {'masquée' if is_hidden(ss) else 'visible'})")
        if norm(notes_text(ss)) and norm(notes_text(ss)) != norm(notes_text(so)):
            rep.err(w, "notes du présentateur absentes ou modifiées")
        if entry["mode"] == "reuse":
            continue
        if entry["mode"] == "design":
            rep.warn(w, f"contenu repris de la slide de design du template ({entry.get('design')}) : "
                        "vérifier qu'il correspond bien à la source")
            continue
        out_txt = norm(" ".join(shape_texts(so))).lower()
        missing = [t for t in shape_texts(ss) if norm(t).lower() not in out_txt]
        if entry["mode"] == "clone":
            missing = []
        out_words = set(re.findall(r"\w+", out_txt))
        moved = [m for m in missing if set(re.findall(r"\w+", norm(m).lower())) <= out_words]
        missing = [m for m in missing if m not in moved]
        accents = [m for m in missing if unaccent(norm(m).lower()) in unaccent(out_txt)]
        missing = [m for m in missing if m not in accents]
        if moved:
            rep.warn(w, "texte réparti (ex. capsule + titre), à vérifier : " +
                     " | ".join(m[:70] for m in moved[:4]))
        if accents:
            rep.warn(w, "accents corrigés par rapport à la source : " +
                     " | ".join(m[:70] for m in accents[:4]))
        if missing:
            rep.err(w, f"{len(missing)} texte(s) source absents / modifiés : " +
                    " | ".join(m[:70] for m in missing[:6]))
    not_used = [i for i in range(1, len(src.slides) + 1) if i not in covered]
    if not_used:
        rep.warn("Document", f"slides source non reprises : {not_used} (volontaire ? à justifier)")
    else:
        rep.ok.append("toutes les slides source sont reprises")
    if not rep.errors:
        rep.ok.append("état masqué, notes et textes conformes")


def en_checks(prs, fr_path, rep):
    fr = open_prs(fr_path)
    if len(fr.slides) != len(prs.slides):
        rep.err("Document", f"{len(prs.slides)} slides EN vs {len(fr.slides)} FR")
    for i, (se, sf) in enumerate(zip(prs.slides, fr.slides), 1):
        w = f"Slide {i}"
        if is_hidden(se) != is_hidden(sf):
            rep.err(w, "état masqué différent du FR")
        if se.slide_layout.name != sf.slide_layout.name:
            rep.err(w, "masque différent du FR (le design ne doit pas changer)")
        if len(list(iter_shapes(se.shapes))) != len(list(iter_shapes(sf.shapes))):
            rep.err(w, "nombre de formes différent du FR")
        for t in shape_texts(se) + [notes_text(se)]:
            hits = FR_WORDS.findall(t)
            if len(hits) >= 2:
                rep.warn(w, f"texte FR résiduel ? « {t[:80]} »")
                break
        nums_fr = sorted(re.findall(r"\d+(?:[.,]\d+)?", " ".join(shape_texts(sf))))
        nums_en = sorted(re.findall(r"\d+(?:[.,]\d+)?", " ".join(shape_texts(se))))
        if nums_fr != nums_en:
            rep.warn(w, f"chiffres différents FR/EN : {set(nums_fr) ^ set(nums_en)}")
        if norm(notes_text(sf)) and not norm(notes_text(se)):
            rep.err(w, "notes non reprises")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--en", help="FR validé de référence (mode traduction)")
    ap.add_argument("--standalone", action="store_true")
    ap.add_argument("--log", help="build_log.json (défaut : retrouvé dans work/)")
    a = ap.parse_args()
    path = Path(a.pptx).resolve()
    prs = open_prs(path)
    rep = Report()
    charte_checks(prs, rep)
    out_dir = None
    if a.en:
        # défauts de charte déjà présents dans le FR validé : non bloquants pour la traduction
        fr_rep = Report()
        charte_checks(open_prs(Path(a.en).resolve()), fr_rep)
        inherited = set(fr_rep.errors)
        rep.warnings += [f"(hérité du FR validé) {e}" for e in rep.errors if e in inherited]
        rep.errors = [e for e in rep.errors if e not in inherited]
        en_checks(prs, Path(a.en).resolve(), rep)
    elif not a.standalone:
        logs = [Path(a.log)] if a.log else [p for p in WORK.rglob("build_log.json")
                                             if Path(json.loads(p.read_text(encoding="utf-8"))["output"]).resolve() == path]
        if not logs:
            sys.exit("build_log.json introuvable : utiliser --log ou --standalone")
        log = json.loads(logs[0].read_text(encoding="utf-8"))
        out_dir = logs[0].parent
        fr_checks(prs, log, rep)
    if out_dir is None:
        out_dir = work_dir(path)
    name = "audit.md" if not a.en else "audit_en.md"
    if a.standalone:
        name = f"audit_{path.stem}.md"
    (out_dir / name).write_text(rep.md(path.name), encoding="utf-8")
    print(f"{len(rep.errors)} erreur(s), {len(rep.warnings)} avertissement(s) -> {out_dir / name}")
    for e in rep.errors[:25]:
        print("  ❌", e)
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
