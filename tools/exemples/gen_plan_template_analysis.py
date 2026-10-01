"""Plan de « FR - Template Analysis V4.1 » (161 slides sources) -> work/<doc>/plan.json

- slides identiques au deck ERP Integration -> spécification validée de tools/exemples/plan_erp_integration.json
- fiches module (22-125) : « Utilisation standard » (texte + capture) / « Customisations » (texte + crayon)
- sections : Contexte · Réussir votre projet · Besoins & Solutions · Offre · Organisation projet
"""
import copy
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from common import emu_in, iter_shapes, norm, open_prs, rel_or_abs, work_dir  # noqa: E402
from pptxops import find_shape  # noqa: E402
from translate import para_text  # noqa: E402

SRC_REL = "02. French PPT to transform/FR - Template Analysis V4.1.potx"
# Usage : python tools/exemples/gen_plan_template_analysis.py [<deck source, ex. fichier joint>]
SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / SRC_REL
src = open_prs(SRC)
erp_spec = {s["src"]: s for s in json.loads((ROOT / "tools/exemples/plan_erp_integration.json")
                                            .read_text(encoding="utf-8"))["slides"] if s.get("src")}
Z = "​"


def erp(erp_n, src_n, zones=None, **kw):
    s = copy.deepcopy(erp_spec[erp_n])
    s.pop("comment", None)
    s["src"] = src_n
    if zones:
        s["zones"].update(zones)
    s.update(kw)
    return s


def section(src_n, num, label, title, caps):
    return {"src": src_n, "mode": "fill", "layout": "Section Title", "method": "section",
            "zones": {"0": title, "1": num, "13": caps}, "section": {"num": num, "label": label}}


def title_of(n):
    for sh in src.slides[n - 1].shapes:
        if sh.is_placeholder and sh.placeholder_format.idx == 0 and sh.has_text_frame:
            return " ".join(x for x in (para_text(p._p).strip() for p in sh.text_frame.paragraphs) if x)
    return ""


def all_but_title(n):
    out, seen = [], {}
    for sh in src.slides[n - 1].shapes:
        if sh.is_placeholder and sh.placeholder_format.idx == 0:
            continue
        if sh.is_placeholder and "SLIDE_NUMBER" in str(sh.placeholder_format.type):
            continue
        if "numéro de diapositive" in sh.name:
            continue
        seen[sh.name] = seen.get(sh.name, 0) + 1
        out.append(sh.name + (f"#{seen[sh.name]}" if seen[sh.name] > 1 else ""))
    return out


def fit_size(shape, width_in, height_in, sizes=(16, 14, 13, 12, 11, 10, 9)):
    """Plus grande taille (pt) pour que le texte tienne dans la zone (estimation prudente)."""
    paras = [para_text(p._p) for p in shape.text_frame.paragraphs if p.text.strip()]
    for s in sizes:
        cpl = max(10, (width_in - 0.6) * 72 / (0.52 * s))
        lines = sum(max(1, math.ceil(len(p) / cpl)) for p in paras)
        # calibré sur le rendu du template (interligne ~ 1,0 × taille ; espacement supprimé si ≤ 11 pt)
        need = lines * s * 1.0 / 72 + (0 if s <= 11 else len(paras) * s * 0.3 / 72)
        if need <= height_in * 0.92:
            return s
    return sizes[-1]


def module_spec(n):
    slide = src.slides[n - 1]
    title = title_of(n)
    texts = [sh for sh in slide.shapes if sh.has_text_frame and norm(sh.text_frame.text)
             and not (sh.is_placeholder and sh.placeholder_format.idx == 0)]
    body = max(texts, key=lambda sh: len(sh.text_frame.text))
    pics = [sh for sh in slide.shapes if sh._element.tag.endswith("}pic")]
    shots = [p for p in pics if emu_in(p.width) > 2]
    pencils = [p for p in pics if emu_in(p.width) <= 1.3]
    spec = {"src": n, "mode": "fill", "zones": {"0": title, "13": "BESOINS COUVERTS"},
            "copy_text": {"1": body.name}, "anchor_top": [1]}
    if shots:
        spec["layout"] = "1_Standard -  2/3 1/3 columns"
        spec["method"] = "fiche module : texte + capture d'écran"
        spec["place"] = [{"shapes": [shots[0].name], "box": [7.83, 2.45, 4.75, 4.3]}]
        size = fit_size(body, 6.75, 4.11)
    else:
        spec["layout"] = "Standard - 1 column"
        spec["method"] = "fiche module : texte" + (" + crayon « à compléter »" if pencils else "")
        size = fit_size(body, 11.81, 4.15)
        if pencils:
            spec["place"] = [{"shapes": [pencils[0].name], "box": [0.18, 2.62, 0.5, 0.52]}]
    spec["font_size"] = {"1": size}
    if size <= 11:
        spec["tight"] = [1]
    return spec


def sticker(n):
    """Post-it interne (zone de texte en haut à droite : « Should be checked… »)."""
    sh = next(sh for sh in src.slides[n - 1].shapes if not sh.is_placeholder and sh.has_text_frame
              and emu_in(sh.top) < 1.5 and emu_in(sh.left) > 8 and norm(sh.text_frame.text))
    h = 1.0 if len(sh.text_frame.text) <= 50 else 1.2          # post-it de 3 lignes : un peu plus haut
    return {"shapes": [sh.name], "box": [8.95, 0.58, 4.1, h], "scale_fonts": False}
slides = [
    {"src": 1, "mode": "fill", "layout": "1_Main Title", "method": "couverture (logo Odoo Gold Partner ancien branding non repris)",
     "zones": {"0": "RAPPORT D’ANALYSE CLIENT"}},
    {"mode": "summary", "layout": "Summary", "zones": {"0": "Sommaire", "13": "SOMMAIRE"},
     "method": "sommaire régénéré depuis les sections (remplace la slide source 2)"},
    {"mode": "fill", "layout": "Section Title", "method": "section créée (1er point du sommaire source)",
     "zones": {"0": "CONTEXTE", "1": "01", "13": "RAPPORT D’ANALYSE"},
     "section": {"num": "01", "label": "Contexte"}},
    erp(12, 3), erp(13, 4), erp(14, 5),
    {"src": 6, "mode": "fill", "layout": "Boxed - 2 columns", "method": "2 éléments parallèles",
     "zones": {"0": "Introduction", "13": "CONTEXTE", "15": "NOTRE BUT", "18": "APPROCHE PROJET"},
     "copy_text": {"16": "ZoneTexte 11", "19": "ZoneTexte 13"},
     "geometry": {"15": [0.96, 2.9, 5.31, 0.6], "16": [0.96, 3.6, 5.31, 2.6],
                  "18": [7.06, 2.9, 5.31, 0.6], "19": [7.06, 3.6, 5.31, 2.6]},
     "font_size": {"16": 14, "19": 14}, "anchor_top": [16, 19],
     "comment": "pictos coche / cible portés par l'ancien masque : non repris"},
    {"src": 7, "mode": "fill", "layout": "Standard - 1 column", "method": "texte + crayons « à compléter »",
     "zones": {"0": "Introduction", "13": "CONTEXTE"}, "copy_text": {"1": "Google Shape;2430;p3"},
     "font_size": {"1": 14}, "anchor_top": [1],
     "place": [{"shapes": ["Graphique 2"], "box": [5.0, 2.45, 0.75, 0.75]},
               {"shapes": ["Graphique 3"], "box": [3.3, 4.3, 0.75, 0.75]}]},
    {"src": 8, "mode": "fill", "layout": "Standard - 1 column", "method": "texte + crayon « à compléter »",
     "zones": {"0": "Vocabulaire", "13": "CONTEXTE"}, "copy_text": {"1": "Google Shape;2430;p3"},
     "font_size": {"1": 14}, "anchor_top": [1],
     "place": [{"shapes": ["Graphique 2"], "box": [3.3, 2.45, 0.75, 0.75]}]},
    section(9, "02", "Réussir votre projet", "NOTRE VISION\nD’UN PROJET RÉUSSI", "VISION"),
    erp(20, 10), erp(21, 11), erp(22, 12), erp(23, 13), erp(25, 14), erp(2, 15),
    erp(3, 16, {"23": "+12M", "20": "+5K", "26": "+47K"}),
    section(17, "03", "Besoins & Solutions", "BESOINS ET SOLUTIONS", "ANALYSE"),
]
for n in (18, 19, 20):
    slides.append({"src": n, "mode": "transplant", "layout": "Standard - Title only - Wide",
                   "method": "5a schéma (image) + lien + crayon", "zones": {"0": title_of(n), "13": "PROCESS"},
                   "include": all_but_title(n), "box": [0.76, 1.7, 11.81, 5.15], "upscale": True})
slides.append({"src": 21, "mode": "fill", "layout": "Design - Arrow down", "method": "intercalaire",
               "zones": {"0": "BESOINS COUVERTS PAR VOTRE NOUVEAU ODOO", "13": "BESOINS & SOLUTIONS"},
               "comment": "illustration Storyset non reprise"})
for n in range(22, 126):
    slides.append(module_spec(n))
slides += [
    {"src": 126, "mode": "fill", "layout": "Design - Arrow down", "method": "intercalaire",
     "zones": {"0": "LISTE DES TÂCHES", "13": "BESOINS & SOLUTIONS"}, "comment": "illustration Storyset non reprise"},
]
for n in (127, 128):
    slides.append({"src": n, "mode": "fill", "layout": "Standard - 2 columns with subititle",
                   "method": "2 colonnes + post-it interne", "zones": {"0": title_of(n), "13": "LISTE DES TÂCHES"},
                   "copy_text": {"1": "Espace réservé du texte 6", "2": "Espace réservé du contenu 7",
                                 "3": "Espace réservé du texte 8", "4": "Espace réservé du contenu 9"},
                   "font_size": {"2": 14, "4": 14}, "anchor_top": [2, 4], "place": [sticker(n)]})
slides += [
    section(129, "04", "Offre", "OFFRE", "BUDGET"),
    erp(34, 130), erp(35, 131), erp(36, 132),
    {"src": 133, "mode": "fill", "layout": "Circles - 2 columns", "method": "2 éléments + post-it interne",
     "zones": {"0": "License Odoo", "13": "APPROCHE BUDGÉTAIRE"},
     "copy_text": {"23": "Espace réservé du texte 3", "26": "Espace réservé du texte 4",
                   "24": "Espace réservé du texte 5", "27": "Espace réservé du texte 5#2",
                   "25": "Espace réservé du texte 5#3"},
     "geometry": {"24": [1.48, 4.87, 4.4, 0.75], "25": [0.76, 5.9, 11.81, 0.8]},
     "font_size": {"23": 20, "26": 20, "24": 12}, "place": [sticker(133)]},
    erp(39, 134, {"25": "110.00 EUR/h HT", "31": "130.00 EUR/h HT", "34": "150.00 EUR/h HT", "28": "180.00 EUR/h HT"}),
    erp(40, 135), erp(41, 136), erp(42, 137),
]
for n in (138, 139):
    slides.append({"src": n, "mode": "fill", "layout": "Standard - 2 columns", "method": "2 colonnes (blocs titrés) + post-it",
                   "zones": {"0": title_of(n), "13": "OFFRE"},
                   "features": {"1": [["Espace réservé du texte 6", "Espace réservé du contenu 7"],
                                      ["Espace réservé du texte 8", "Espace réservé du contenu 9"]],
                                "2": [["Espace réservé du texte 4", "Espace réservé du contenu 17"]]},
                   "heading_size": 16, "text_size": 13, "anchor_top": [1, 2],
                   "place": [sticker(n), {"shapes": ["Espace réservé du texte 15"], "box": [8.75, 4.85, 1.85, 1.85],
                                          "badge": True}]})
for n, caps in ((140, "OFFRE"), (141, "OFFRE")):
    slides.append({"src": n, "mode": "fill", "layout": "Standard - 1 column", "method": "texte",
                   "zones": {"0": title_of(n), "13": caps}, "copy_text": {"1": all_but_title(n)[0]},
                   "font_size": {"1": 15}, "anchor_top": [1]})
slides += [
    section(142, "05", "Organisation projet", "VOTRE PROJET", "ORGANISATION PROJET"),
    erp(16, 143), erp(17, 144),
    {"src": 145, "mode": "transplant", "layout": "Standard - Title only", "method": "5d tableau",
     "zones": {"0": "Rôles", "13": "ORGANISATION PROJET"}, "box": [0.76, 2.6, 11.81, 4.2], "upscale": True},
    erp(30, 146), erp(31, 147),
    {"src": 148, "mode": "fill", "layout": "Standard - 1 column", "method": "texte",
     "zones": {"0": "Formation des key users", "13": "MISE EN PRODUCTION"},
     "copy_text": {"1": "Content Placeholder 6"}, "font_size": {"1": 16}, "anchor_top": [1]},
    {"src": 149, "mode": "fill", "layout": "Design - Circle left", "method": "texte",
     "zones": {"0": "Période UAT", "13": "MISE EN PRODUCTION"}, "copy_text": {"14": "Content Placeholder 6"},
     "font_size": {"14": 18}},
]
for n, shape in ((150, "Diagram 3"), (151, "Diagram 1"), (152, "Content Placeholder 1")):
    slides.append({"src": n, "mode": "transplant", "layout": "Standard - Title only", "method": "5a SmartArt",
                   "zones": {"0": title_of(n), "13": "MISE EN PRODUCTION"}, "include": [shape],
                   "box": [0.76, 2.55, 11.81, 4.3], "upscale": True})
for n, caps, title in ((153, "ORGANISATION PROJET", "Communication projet"),
                       (154, "IMPLICATION PROJET", "Pilotage"), (155, "IMPLICATION PROJET", "Projet"),
                       (156, "IMPLICATION PROJET", "UAT et formations")):
    slides.append({"src": n, "mode": "transplant", "layout": "Standard - Title only", "method": "5d tableau (+ crayons)",
                   "zones": {"0": title, "13": caps}, "box": [0.76, 2.55, 11.81, 4.3], "upscale": True})
for n, caps, title in ((157, "INDICATEURS DE SUIVI", "Hebdomadaire"), (158, "INDICATEURS DE SUIVI", "Mensuels"),
                       (159, "PILOTAGE", "Indicateurs de suivi")):
    slides.append({"src": n, "mode": "fill", "layout": "Standard - 1 column", "method": "texte (mises en valeur conservées)",
                   "zones": {"0": title, "13": caps}, "copy_text": {"1": "Espace réservé du contenu 2"},
                   "keep_color": [1], "font_size": {"1": fit_size(find_shape(src.slides[n - 1], "Espace réservé du contenu 2"), 11.81, 4.15)},
                   "anchor_top": [1]})
slides += [
    {"src": 160, "mode": "fill", "layout": "3_Circles - 2 columns X2", "method": "slide de clôture",
     "zones": {"0": "QUELLES SONT VOS QUESTIONS ?", "13": "ÉCHANGES"}, "comment": "illustration Storyset non reprise"},
    {"src": 161, "mode": "design", "design": "bureaux_fr", "method": "slide de design du template (Nos bureaux)"},
]


def main():
    errors = []
    for sp in slides:
        n = sp.get("src")
        if not n or sp.get("mode") == "design":
            continue
        sl = src.slides[n - 1]
        names = list(sp.get("include") or []) + list(sp.get("copy_text", {}).values())
        names += [x for pl in sp.get("place", []) for x in pl["shapes"]]
        names += [x for groups in sp.get("features", {}).values() for g in groups for x in g if x]
        for nm in names:
            try:
                find_shape(sl, nm)
            except KeyError:
                errors.append((n, nm))
    plan = {"source": rel_or_abs(SRC), "output": "04. Render from claude/FR - Template Analysis V4.1.pptx",
            "lang": "fr", "slides": slides}
    out = work_dir(SRC) / "plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    covered = sorted(s["src"] for s in slides if s.get("src"))
    from collections import Counter
    print(len(slides), "slides ->", out)
    print("sources non couvertes :", sorted(set(range(1, len(src.slides) + 1)) - set(covered)))
    print("formes introuvables :", errors)
    print(Counter(f"{s.get('mode')}:{s.get('layout') or s.get('design')}" for s in slides).most_common())


if __name__ == "__main__":
    main()
