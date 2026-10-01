"""EXEMPLE — génère le plan de « EN - Sales - MMB Market » (document déjà en anglais : pas de traduction).

Usage : python tools/exemples/gen_plan_mmb_market.py   -> work/<doc>/plan.json
Les slides équivalentes au deck ERP reprennent la spécification validée du plan ERP
(tools/exemples/plan_erp_integration.json : masque, placements, icônes) avec les textes anglais MMB.
Vérifie que chaque forme citée existe dans la source.
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # tools/exemples
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from common import open_prs, rel_or_abs, work_dir  # noqa: E402
from pptxops import find_shape  # noqa: E402

SRC_REL = "02. French PPT to transform/Sales knowledge/03. ERP Ressources Allocation Offer/EN - Sales - MMB Market.potx"
erp_spec = {s["src"]: s for s in json.loads((HERE / "plan_erp_integration.json").read_text(encoding="utf-8"))["slides"]
            if s.get("src")}
# Usage : python tools/exemples/gen_plan_mmb_market.py [<deck source, ex. fichier joint>]
SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / SRC_REL
src = open_prs(SRC)
Z = "​"


def erp(n, src_n, zones=None, **kw):
    s = copy.deepcopy(erp_spec[n])
    s.pop("comment", None)
    s["src"] = src_n
    s["zones"] = zones if zones is not None else {}
    s.update(kw)
    return s


def section(src_n, num, label, title, caps):
    return {"src": src_n, "mode": "fill", "layout": "Section Title", "method": "section",
            "zones": {"0": title, "1": num, "13": caps}, "section": {"num": num, "label": label}}


def all_but(n, *names):
    """Toutes les formes de 1er niveau sauf titre / numéro de slide / noms donnés."""
    out = []
    for sh in src.slides[n - 1].shapes:
        if sh.is_placeholder and ("TITLE" in str(sh.placeholder_format.type)
                                  or "SLIDE_NUMBER" in str(sh.placeholder_format.type)):
            continue
        if "numéro de diapositive" in sh.name or sh.name in names:
            continue
        out.append(sh)
    names_out, seen = [], {}
    for sh in out:
        seen[sh.name] = seen.get(sh.name, 0) + 1
        names_out.append(sh.name + (f"#{seen[sh.name]}" if seen[sh.name] > 1 else ""))
    return names_out


slides = [
    {"src": 1, "mode": "fill", "layout": "1_Main Title", "method": "cover",
     "zones": {"0": "ODOO INTEGRATOR FOR YOUR ERP PROJECT"}},
    {"mode": "summary", "layout": "Summary", "zones": {"0": "TABLE OF CONTENTS", "13": "TABLE OF CONTENTS"}},
    {"mode": "fill", "layout": "Section Title", "method": "section créée",
     "zones": {"0": "CAPTIVEA AND ODOO", "1": "01", "13": "DISCOVER US"},
     "section": {"num": "01", "label": "Captivea and Odoo"}},
    erp(2, 2, {"0": "ODOO", "13": "THE SOLUTION"}),
    erp(3, 3, {"0": "ONE SOFTWARE, ONE SUCCESS STORY", "13": "ODOO", "23": "+15M", "24": "USERS",
               "20": "+6K", "21": "EMPLOYEES", "26": "+50K", "27": "MODULES"}),
    erp(4, 4, {"0": "CAPTIVEA", "13": "EXPERTISE", "23": "ERP", "29": "WEB", "32": "AI", "26": "BI"}),
    erp(5, 5, {"0": "WORLDWIDE LEADER ODOO INTEGRATOR", "13": "CAPTIVEA", "23": "+800", "24": "HAPPY CUSTOMERS",
               "20": "+200", "21": "MOTIVATED EMPLOYEES", "26": "+18", "27": "YEARS OF INTEGRATION"}),
    erp(10, 6, {"0": "OUR REFERENCES", "13": "REFERENCES"}),
    erp(12, 7, {"0": "CAPTIVEA’S PROJECT TIMELINE", "13": "TIMELINE", "23": Z, "29": Z, "32": Z, "26": Z,
                "24": ["FREE", "CONSULTATION"], "30": ["GLOBAL", "ESTIMATION"], "33": ["ANALYSIS", "PHASE"],
                "27": "IMPLEMENTATION PHASE"}),
    {"src": 8, "mode": "transplant", "layout": "Standard - Title only - Wide", "method": "5a schéma",
     "zones": {"0": "EVOLVE WITH ODOO", "13": "EVOLUTION"}, "include": None, "exclude": ["Titre 4", "Forme libre : forme 38"],
     "box": [0.76, 1.75, 11.81, 5.0],
     "upscale": True},
    erp(15, 9, {"0": "CAPTIVEA PROJECT GOVERNANCE", "13": "GOVERNANCE", "23": Z, "20": Z, "26": Z,
                "24": "WEEKLY DEMO MEETING", "21": "WEEKLY PROJECT MANAGEMENT MEETING",
                "27": "STEERING COMMITTEES ON REQUEST"}),
    section(10, "02", "Demonstration", "DEMONSTRATION", "ONE SOFTWARE, ONE SUCCESS STORY"),
    section(11, "03", "Our vision of a succesful project", "OUR VISION OF\nA SUCCESFUL PROJECT", "VISION"),
    erp(20, 12, {"0": "GO LIVE AS SOON AS POSSIBLE", "13": "VISION", "23": "1", "20": "2", "26": "3",
                 "24": "STAY CLOSE TO THE STANDARD", "21": "DEFINE A MVP", "27": "IMPLEMENTATION ANALYSIS"}),
    {"src": 13, "mode": "transplant", "layout": "Standard - Title only", "method": "5a schéma (2 équipes liées)",
     "zones": {"0": "LET’S MOVE FORWARD TOGETHER!", "13": "COLLABORATION"},
     "include": "ALL", "box": [0.76, 2.55, 11.81, 4.2], "upscale": True, "recolor_all_icons": True},
    erp(22, 14, {"0": "FEEL FREE TO CHANGE YOUR MIND WITH FULL TRANSPARENCY!", "13": "FLEXIBILITY",
                 "23": "1", "20": "2", "26": "3", "24": "FUNCTIONAL SCOPE", "21": "TIMELINE", "27": "SERVICE LEVEL"}),
    erp(23, 15, {"0": "BENEFIT FROM ALL OUR EXPERTISE", "13": "EXPERTISE"}),
    erp(24, 16, {"0": "SLA\nMaintenance & Support", "13": "SUPPORT"}),
    erp(25, 17, {"0": "THE STEPS TO SUCCESS- GOVERNANCE", "13": "METHODOLOGY"}),
    section(18, "04", "We provide you off & on-site ressources", "WE PROVIDE YOU\nOFF & ON-SITE RESSOURCES", "RESSOURCES"),
    {"src": 19, "mode": "fill", "layout": "Boxed - 3 columns X2", "method": "6 profils parallèles",
     "zones": {"0": "ROLES & AVAILABLE RESSOURCES", "13": "RESSOURCES",
               "15": "Project Manager", "21": "Enterprise consultant", "18": "Business Analyst ",
               "24": "Configurator", "30": "Developer", "27": "Architect"},
     "place": [{"shapes": ["Graphique 66"], "box": [0.96, 3.45, 3.35, 1.1]},
               {"shapes": ["Graphique 70"], "box": [4.99, 3.45, 3.35, 1.1]},
               {"shapes": ["Graphique 74"], "box": [9.03, 3.45, 3.35, 1.1]},
               {"shapes": ["Graphique 72"], "box": [0.96, 5.6, 3.35, 1.1]},
               {"shapes": ["Graphique 68"], "box": [4.99, 5.6, 3.35, 1.1]},
               {"shapes": ["Graphique 62"], "box": [9.03, 5.6, 3.35, 1.1]}],
     "geometry": {"15": [0.96, 2.8, 3.35, 0.6], "21": [4.99, 2.8, 3.35, 0.6], "18": [9.03, 2.8, 3.35, 0.6],
                  "24": [0.96, 4.95, 3.35, 0.6], "30": [4.99, 4.95, 3.35, 0.6], "27": [9.03, 4.95, 3.35, 0.6]}},
    erp(16, 20, {"0": "TEAM PROJECT", "13": "TEAM"}, include=["Graphique 3"]),
    erp(17, 21, {"0": "ROLES DEFINITION", "13": "PROJECT TEAM"}),
    {"src": 22, "mode": "transplant", "layout": "Standard - Title only - Wide", "method": "5a schéma (équipes)",
     "zones": {"0": "BUILD YOUR OWN CAPTIVEA TEAM!", "13": "TEAM"}, "box": [0.76, 1.65, 11.81, 5.2], "upscale": True},
    {"src": 23, "mode": "transplant", "layout": "Standard - Title only - Wide", "method": "5a planning (Gantt)",
     "zones": {"0": "BUILD YOUR OWN CAPTIVEA TEAM!", "13": "TEAM PLANNING"}, "box": [0.76, 1.65, 11.81, 5.2],
     "upscale": True},
    section(24, "05", "We implement ERP in North America, Europe & Asia",
            "WE IMPLEMENT ERP IN\nNORTH AMERICA, EUROPE & ASIA", "WORLDWIDE"),
]
for n in (25, 26, 27, 28):
    slides.append({"src": n, "mode": "transplant", "layout": "Design - Circle left", "method": "fiche ressources client",
                   "zones": {"13": "CASE STUDY", "0": "CAPTIVEA’S RESSOURCES"},
                   "copy_text": {"25": "Sous-titre 6"}, "include": "ALL_BUT:Sous-titre 6",
                   "box": [6.4, 0.7, 6.4, 6.1], "upscale": True,
                   "geometry": {"0": [0.76, 1.45, 4.5, 1.6], "25": [0.76, 3.2, 4.6, 3.5]}, "anchor_top": [25]})
slides += [
    {"src": 29, "mode": "transplant", "layout": "Standard - Title only", "method": "logos + chiffres",
     "zones": {"0": "OTHER MMB IMPLEMENTATIONS", "13": "REFERENCES"}, "include": "ALL",
     "box": [0.76, 2.55, 11.81, 4.2], "upscale": True},
    section(30, "06", "Business analysis", "BUSINESS ANALYSIS", "ANALYSIS"),
    erp(27, 31, {"0": "PROGRESS OF THE ANALYSIS", "13": "BUSINESS ANALYSIS"}),
    erp(28, 32, {"0": "DELIBRABLE AT THE END OF AN ANALYSIS", "13": "BUSINESS ANALYSIS"}),
    section(33, "07", "Implementation phase & go-live", "IMPLEMENTATION PHASE\n& GO-LIVE", "IMPLEMENTATION"),
    erp(30, 34, {"0": "IMPLEMENTATION PHASE", "13": "IMPLEMENTATION"}),
    erp(31, 35, {"0": "GO-LIVE", "13": "IMPLEMENTATION"}),
    section(36, "08", "Budget approach", "BUDGET APPROACH", "BUDGET"),
    erp(34, 37, {"0": "LOCAL, HYBRIDE OR OFFSHORE PROJECT MODE", "13": "BUDGET APPROACH",
                 "23": Z, "20": Z, "26": Z, "24": "LOCAL", "21": "HYBRID", "27": "OFFSHORE"}),
    erp(35, 38, {"0": "OUR PRICING OFFER", "13": "BUDGET APPROACH", "23": Z, "29": Z, "32": Z, "26": Z,
                 "24": "ANALYSIS", "33": "IMPLEMENTATION", "27": "ADDITIONAL MODULE PURCHASES"}),
    erp(36, 39, {"0": "VARIOUS ODOO HOSTING OPTIONS", "13": "HOSTING"}),
    erp(37, 40, {"0": "BUDGET APPROACH", "13": "LICENSES & HOSTING",
                 "23": ["Odoo", "Licences"], "26": ["Odoo.SH", "Hosting"],
                 "24": ["29,90€ /m/User the 1st year", "37,40€ /m/user the next year"], "27": "29,90€ /month"}),
]
levels = {
    41: ("USA", ["125 USD/h HT"], ["138 USD/h HT"], ["150 USD/h HT"], ["180 USD/h HT"]),
    42: ("SINGAPORE", ["100 SGD/h HT"], ["150 SGD/h HT"], ["180 SGD /h HT"], ["200 SGD/h HT"]),
    43: ("CANADA", ["140 CAD /H HT"], ["180 CAD /h HT"], ["200 CAD /h HT"], ["225 CAD /h HT"]),
    44: ("INDIA", ["18 USD/h HT", "1000 INR/h HT"], ["25 USD /h HT", "1500 INR/h HT"],
         ["32 USD /h HT", "2000 INR/h HT"], ["34 USD/h HT", "2500 INR/h HT"]),
    45: ("LUXEMBOURG", ["120 EUR/h HT"], ["138 EUR/h HT"], ["155 EUR/h HT"], ["180 EUR/h HT"]),
}
for n, (country, a, b, c, d) in levels.items():
    slides.append(erp(39, n, {"0": f"OUR EXPERTISE LEVELS - {country}", "13": "BUDGET APPROACH",
                              "23": Z, "29": Z, "32": Z, "26": Z,
                              "24": "Consultant / Odoo Developer", "25": a,
                              "30": "Consultant / Certified Odoo Developer", "31": b,
                              "33": "Consultant / Senior Odoo Developer", "34": c,
                              "27": "Consultant / Odoo Legendary Developer", "28": d}))
slides += [
    erp(43, 46, {"0": "ANALYSIS PHASE", "13": "BUDGET APPROACH"},
        copy_text={"1": "Espace réservé du texte 10", "2": "Rectangle 2",
                   "3": "Espace réservé du texte 4", "4": "Espace réservé du contenu 17"}),
    erp(44, 47, {"0": "IMPLEMENTATION", "13": "BUDGET APPROACH"}),
    erp(47, 48, {}),
    {"src": 49, "mode": "design", "design": "bureaux_en", "method": "slide de design du template (Our offices, EN)"},
]


def main():
    errors = []
    for sp in slides:
        n = sp.get("src")
        if not n:
            continue
        sl = src.slides[n - 1]
        inc = sp.get("include")
        if inc == "ALL":
            sp["include"] = all_but(n)
        elif isinstance(inc, str) and inc.startswith("ALL_BUT:"):
            sp["include"] = all_but(n, *inc.split(":", 1)[1].split("|"))
        elif inc is None:
            sp.pop("include", None)
        if sp.pop("recolor_all_icons", False):
            sp["recolor"] = {"color": "BA131A", "shapes": [x.split("#")[0] for x in sp["include"] if "Google Shape" in x]}
        names = list(sp.get("include") or []) + list(sp.get("copy_text", {}).values())
        names += [x for pl in sp.get("place", []) for x in pl["shapes"]]
        for nm in names:
            try:
                find_shape(sl, nm)
            except KeyError:
                errors.append((n, nm))
        for ex in sp.get("exclude", []):
            if not any(ex == sh.name for sh in sl.shapes):
                errors.append((n, "exclude:" + ex))
    plan = {"source": rel_or_abs(SRC),
            "output": "04. Render from claude/Sales knowledge/03. ERP Ressources Allocation Offer/EN - Sales - MMB Market.pptx",
            "lang": "en", "slides": slides}
    out = work_dir(SRC) / "plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", out)
    covered = sorted(s["src"] for s in slides if s.get("src"))
    print(len(slides), "slides · sources manquantes :", sorted(set(range(1, 50)) - set(covered)))
    print("formes introuvables :", errors)


if __name__ == "__main__":
    main()
