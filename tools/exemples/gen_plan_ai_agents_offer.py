"""Plan de « FR - Sales - AI Agents Offer » -> work/<doc>/plan.json

Base : la version corrigée par François (05, faite sur un ancien template 2026), pas la source brute 02.
Ses masques et zones sont identiques à ceux du template : les slides de contenu sont clonées sur le
masque du même nom (mise en forme de François conservée). Couverture, sommaire et sections sont refaits
avec les slides de design (couverture sans capsule, numéro de section en zone 1, sommaire généré).

La version de François est cherchée, dans l'ordre : 05. Render corrected/ (dépôt direct, claude.ai),
05. Render corrected/Sales knowledge/09. AI Agents Offer/, puis le 05 du dossier parent de PROJECT.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # tools/exemples
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from common import open_prs, rel_or_abs, work_dir  # noqa: E402

NAME = "FR - Sales - AI Agents Offer.pptx"
SUB = "Sales knowledge/09. AI Agents Offer"
CANDIDATES = [ROOT / "05. Render corrected" / NAME,
              ROOT / "05. Render corrected" / SUB / NAME,
              ROOT.parent / "05. Render corrected" / SUB / NAME]
# Usage : python tools/exemples/gen_plan_ai_agents_offer.py [<version corrigée par François>]
if len(sys.argv) > 1:
    found = Path(sys.argv[1]).resolve()
else:
    found = next((p for p in CANDIDATES if p.exists()), None)
if found is None:
    sys.exit("Version corrigée par François introuvable : la déposer dans « 05. Render corrected/ » "
             f"({NAME}).")
_prs = open_prs(found)
if len(_prs.slides) != 26 or _prs.slides[1].slide_layout.name != "Summary":
    sys.exit(f"{found.name} n'est pas la version corrigée par François (26 slides, sommaire en slide 2) : "
             "c'est probablement la source brute. Joindre la version 05 de François.")
SOURCE = rel_or_abs(found)


def clone(n, method="clone 05 sur le masque du même nom", **kw):
    return {"src": n, "mode": "clone", "method": method, **kw}


def section(n, num, label, capsule, extra=None):
    return {"src": n, "mode": "fill", "layout": "Section Title",
            "method": "section refaite (numéro en zone 1)",
            "copy_text": {"0": "Title 1"},
            "zones": {"1": [num] + ([extra] if extra else []), "13": capsule},
            "section": {"num": num, "label": label}}


slides = [
    {"src": 1, "mode": "fill", "layout": "1_Main Title", "method": "couverture (sans capsule)",
     "copy_text": {"0": "Title 1", "1": "Subtitle 2"}},
    {"mode": "summary", "layout": "Summary", "zones": {"0": "Sommaire", "13": "SOMMAIRE"},
     "method": "sommaire régénéré depuis les sections (celui du 05 listait les sections d'un autre deck)"},
    section(3, "01", "Captivea et Odoo", "NOUS DÉCOUVRIR"),
    clone(4), clone(5), clone(6),
    section(7, "02", "Découvrir l’IA", "IA"),
    clone(8), clone(9), clone(10), clone(11), clone(12),
    section(13, "03", "6 agents IA entraînés", "IA",
            extra="Chacun prend une charge précise. Vous gardez la main."),
    *[clone(n) for n in range(14, 21)],
    clone(21, method="clone 05, capsule corrigée (6 ANGENTS IA)", zones={"13": "6 AGENTS IA"}),
    clone(22), clone(23),
    clone(24, method="clone 05, capsule harmonisée (accent)", zones={"13": "APPROCHE BUDGÉTAIRE"}),
    clone(25), clone(26),
]

plan = {"source": SOURCE, "output": "04. Render from claude/FR - Sales - AI Agents Offer.pptx",
        "lang": "fr", "slides": slides}
if __name__ == "__main__":
    out = work_dir(ROOT / "02. French PPT to transform" / NAME) / "plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"source : {SOURCE}")
    print(f"{len(slides)} slides -> {out}")
