"""EXEMPLE — génère le plan de « FR - Template - Update Odoo version » (240 slides sources).

Usage : python tools/exemples/gen_plan_erp_upgrade.py   -> work/<doc>/plan.json
Prérequis : la source dans 02 et le rendu FR du deck ERP Integration dans 04
            (construit avec tools/exemples/plan_erp_integration.json : ses slides sont réutilisées).

- slides identiques au deck ERP (texte strictement identique) -> reuse depuis le rendu ERP de 04
- intercalaires "ODOO APPS" (masque source "arrow right") -> Design - Arrow down
- fiches "ODOO xx - APP" -> Standard - 2 columns (ou 1 column) via "features"
- slides propres au document -> spécifications manuelles ci-dessous
Modèle à suivre pour tout gros deck répétitif.
"""
import copy
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # tools/exemples
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from common import emu_in, iter_shapes, norm, open_prs, rel_or_abs, shape_texts, work_dir  # noqa: E402
from translate import para_text  # noqa: E402

SRC_REL = "02. French PPT to transform/Sales knowledge/02. ERP Upgrade Odoo/FR - Template - Update Odoo version.potx"
ERP_PLAN = HERE / "plan_erp_integration.json"

# Usage : python tools/exemples/gen_plan_erp_upgrade.py [<deck Upgrade> [<deck source ERP Integration>
#                                                        [<ERP Integration au nouveau design>]]]
# (les slides communes sont reprises du rendu ERP Integration : il faut ces deux fichiers en plus)
ARGS = [Path(a).resolve() for a in sys.argv[1:]]
SRC = ARGS[0] if len(ARGS) > 0 else ROOT / SRC_REL
src = open_prs(SRC)
erp_plan = json.loads(ERP_PLAN.read_text(encoding="utf-8"))
ERP_SRC = ARGS[1] if len(ARGS) > 1 else ROOT / erp_plan["source"]
ERP_OUT = rel_or_abs(ARGS[2] if len(ARGS) > 2 else ROOT / erp_plan["output"])
for _p, _what in ((ERP_SRC, "le deck source « FR - Sales - ERP Integration Offer »"),
                  (ROOT / ERP_OUT, "ERP Integration Offer au nouveau design (le transformer d'abord)")):
    if not _p.exists():
        sys.exit(f"Fichier requis introuvable : {_what} ({_p})")
erp_src = open_prs(ERP_SRC)
erp_spec = {s["src"]: s for s in erp_plan["slides"] if s.get("src")}
erp_out = {s["src"]: i for i, s in enumerate(erp_plan["slides"], 1) if s.get("src")}   # n° dans le rendu


def sig(s):
    return tuple(sorted(norm(t) for t in shape_texts(s)))


erp_sig = {}
for i, s in enumerate(erp_src.slides, 1):
    erp_sig.setdefault(sig(s), i)


def title_of(slide):
    for sh in slide.shapes:
        if sh.is_placeholder and "TITLE" in str(sh.placeholder_format.type) and sh.has_text_frame:
            return " ".join(x for x in (para_text(p._p) for p in sh.text_frame.paragraphs) if x).replace("\xa0", " ").strip()
    return ""


SECTIONS = {  # n° source -> (numéro, libellé sommaire, titre, capsule)
    11: ("02", "Mettre à jour votre ERP Odoo", "METTRE À JOUR VOTRE ERP ODOO", "MISE À JOUR"),
    15: ("03", "Quelles sont les nouveautés sur Odoo", "QUELLES SONT\nLES NOUVEAUTÉS SUR ODOO", "NOUVEAUTÉS"),
    220: ("04", "Démonstration", "DÉMONSTRATION", "UN LOGICIEL, UNE SUCCESS STORY"),
    221: ("05", "Notre vision d’un projet réussi", "NOTRE VISION\nD’UN PROJET RÉUSSI", "VISION"),
    227: ("06", "Etapes de projet", "ETAPES DE\nPROJET", "MÉTHODOLOGIE"),
    231: ("07", "Approche budgétaire", "APPROCHE BUDGÉTAIRE", "BUDGET"),
}


def section(n):
    num, label, title, caps = SECTIONS[n]
    return {"src": n, "mode": "fill", "layout": "Section Title", "method": "section",
            "zones": {"0": title, "1": num, "13": caps}, "section": {"num": num, "label": label}}


def from_erp(erp_n, **changes):
    s = copy.deepcopy(erp_spec[erp_n])
    s.pop("comment", None)
    for k, v in changes.items():
        if k == "zones":
            s["zones"].update(v)
        else:
            s[k] = v
    return s


def ref(slide, target):
    """Référence unique "Nom" / "Chemin" + "#n" compatible avec pptxops.find_shape."""
    hits = [sh for sh, _, path in iter_shapes(slide.shapes) if target[1] in (path, sh.name)]
    k = next(i for i, sh in enumerate(hits, 1) if sh._element is target[0]._element)
    return target[1] + (f"#{k}" if k > 1 else "")


def features_spec(n, slide):
    title = title_of(slide)
    m = re.match(r"^(ODOO \d+)\s*[-–]\s*(.+)$", title, re.I)
    version, app = (m.group(1), m.group(2).strip()) if m else (title, "NOUVEAUTÉS")
    items, foot = [], []
    for top in slide.shapes:
        base_left = emu_in(top.left) + emu_in(top.width) / 2
        base_top = emu_in(top.top)
        for sh, depth, path in iter_shapes([top]):
            if not sh.has_text_frame or not norm(sh.text_frame.text):
                continue
            if sh.is_placeholder and ("TITLE" in str(sh.placeholder_format.type)
                                      or "SLIDE_NUMBER" in str(sh.placeholder_format.type)):
                continue
            if re.search(r"num[ée]ro de diapositive", sh.name, re.I):
                continue
            h, w = emu_in(sh.height), emu_in(sh.width)
            y = emu_in(sh.top)
            words = len(norm(sh.text_frame.text).split())
            if depth == 0 and w > 9 and y > 6.3:
                foot.append(ref(slide, (sh, path)))
                continue
            nm = sh.name.lower()
            if "contenu" in nm:
                heading = False
            elif "texte" in nm and "zonetexte" not in nm.replace(" ", ""):
                heading = True
            else:
                heading = h <= 0.62 and words <= 12 and len(
                    [p for p in sh.text_frame.paragraphs if norm(p.text)]) == 1
            col = 1 if base_left < 6.67 else 2
            order = (base_top, y) if depth else (y, 0)
            items.append((col, order, heading, ref(slide, (sh, path)), words))
    cols = {1: [], 2: []}
    for col, order, heading, name, _ in sorted(items, key=lambda t: (t[0], t[1])):
        if heading or not cols[col]:
            cols[col].append([name] if heading else [None, name])
        else:
            cols[col][-1].append(name)
    total_words = sum(t[4] for t in items)
    spec = {"src": n, "mode": "fill", "method": "fiche fonctionnalités (titres + descriptions verbatim)",
            "zones": {"0": version, "13": app}}
    if cols[1] and cols[2]:
        spec["layout"] = "Standard - 2 columns"
        spec["features"] = {"1": cols[1], "2": cols[2]}
    else:
        spec["layout"] = "Standard - 1 column"
        spec["features"] = {"1": cols[1] or cols[2]}
    if total_words <= 110:
        spec["heading_size"], spec["text_size"] = 16, 12.5
    elif total_words <= 170:
        spec["heading_size"], spec["text_size"] = 14, 11
    else:
        spec["heading_size"], spec["text_size"] = 12.5, 10
    if foot:
        spec["place"] = [{"shapes": foot, "box": [0.76, 6.62, 11.81, 0.3], "upscale": False}]
        spec["geometry"] = {k: None for k in spec["features"]}
    spec["anchor_top"] = [int(k) for k in spec["features"]]
    return spec


MANUAL = {
    1: {"src": 1, "mode": "fill", "layout": "1_Main Title", "method": "couverture",
        "zones": {"0": "METTRE A JOUR VOTRE ERP ODOO"}},
    3: from_erp(3, src=3, zones={"23": "+15M", "20": "+6K", "26": "+50K"}),
    5: from_erp(5, src=5, zones={"26": "+18"}),
    10: {"src": 10, "mode": "fill", "layout": "Standard - 1 column", "method": "texte",
         "zones": {"0": "COMMENT FONCTIONNE LES VERSIONS ODOO ?", "13": "VERSIONS ODOO"},
         "copy_text": {"1": "Espace réservé du contenu 10"},
         "comment": "illustration Storyset non reprise"},
    12: {"src": 12, "mode": "fill", "layout": "Circles - 3 columns", "method": "texte",
         "zones": {"0": "AMÉLIOREZ LA PRODUCTIVITÉ DE VOTRE ENTREPRISE", "13": "MISE À JOUR",
                   "23": "1", "20": "2", "26": "3",
                   "24": "Améliorez la productivité de vos utilisateurs",
                   "21": "Améliorer La performance de votre entreprise",
                   "27": "Maintenir une solution durable"}},
    13: {"src": 13, "mode": "fill", "layout": "Circles - 3 columns", "method": "texte",
         "zones": {"0": "RESTEZ AU TOP TECHNIQUEMENT", "13": "MISE À JOUR",
                   "23": "1", "20": "2", "26": "3",
                   "24": "Gardez vos accès à Odoo Support & Odoo.sh",
                   "21": "Réduire la dette technique",
                   "27": "Améliorer la sécurité de vos données"}},
    233: from_erp(39, src=233, zones={"25": "110.00 EUR/h HT", "31": "130.00 EUR/h HT",
                                      "34": "150.00 EUR/h HT", "28": "180.00 EUR/h HT"}),
    238: from_erp(44, src=238),
    240: from_erp(48, src=240),          # Nos bureaux : slide de design du template
}
for n, phase in ((228, "PHASE 1"), (229, "PHASE 2"), (230, "PHASE 3")):
    MANUAL[n] = {"src": n, "mode": "transplant", "layout": "Design - Circle left", "method": "5a (étapes + pictos)",
                 "zones": {"13": phase}, "copy_text": {"0": "Espace réservé du texte 1", "25": "Titre 5"},
                 "box": [6.5, 0.6, 6.3, 6.3], "upscale": True,
                 "font_size": {"0": 30}, "geometry": {"0": [0.76, 1.45, 4.5, 2.9]}, "anchor_top": [0],
                 "recolor": None}


def main():
    slides = []
    for n, s in enumerate(src.slides, 1):
        if n == 2:  # sommaire + 1re section juste après la couverture
            slides.append({"mode": "summary", "layout": "Summary", "zones": {"0": "SOMMAIRE", "13": "SOMMAIRE"}})
            slides.append({"mode": "fill", "layout": "Section Title", "method": "section créée",
                           "zones": {"0": "CAPTIVEA ET ODOO", "1": "01", "13": "NOUS DÉCOUVRIR"},
                           "section": {"num": "01", "label": "Captivea et Odoo"}})
        if n in SECTIONS:
            slides.append(section(n))
            continue
        if n in MANUAL:
            spec = MANUAL[n]
            spec.pop("recolor", None) if spec.get("recolor") is None else None
            slides.append(spec)
            continue
        j = erp_sig.get(sig(s))
        if j and sig(s):
            slides.append({"src": n, "mode": "reuse", "from": ERP_OUT, "slide": erp_out[j],
                           "method": f"slide identique au deck ERP (source ERP {j})"})
            continue
        if s.slide_layout.name.strip().lower() == "arrow right":
            texts = [x for sh in s.shapes if sh.has_text_frame and not re.search("num[ée]ro", sh.name)
                     for x in (para_text(p._p).strip() for p in sh.text_frame.paragraphs) if x]
            caps, title = (texts[0], texts[1]) if len(texts) > 1 else ("ODOO APPS", texts[0])
            slides.append({"src": n, "mode": "fill", "layout": "Design - Arrow down", "method": "intercalaire application",
                           "zones": {"0": title, "13": caps}})
            continue
        if re.match(r"^ODOO \d+", title_of(s), re.I):
            slides.append(features_spec(n, s))
            continue
        slides.append({"src": n, "mode": "TODO", "comment": f"non classée : {title_of(s)!r}"})
    # nettoyage des géométries factices
    for sp in slides:
        if sp.get("geometry") and all(v is None for v in sp["geometry"].values()):
            sp["geometry"] = {k: [0.76 if k == "1" else 6.91, 2.59, 5.67 if len(sp["features"]) == 2 else 11.81, 3.95]
                              for k in sp["features"]}
    plan = {"source": rel_or_abs(SRC),
            "output": "04. Render from claude/Sales knowledge/02. ERP Upgrade Odoo/FR - Template - Update Odoo version.pptx",
            "lang": "fr", "slides": slides}
    out = work_dir(SRC) / "plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", out)
    todo = [s for s in slides if s.get("mode") == "TODO"]
    from collections import Counter
    print(len(slides), "slides ·", Counter(s.get("mode") + ":" + str(s.get("layout")) for s in slides).most_common())
    print("TODO:", [(s["src"], s["comment"]) for s in todo])


if __name__ == "__main__":
    main()
