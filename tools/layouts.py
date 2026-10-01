"""Catalogue du template de référence : masques (layouts) + slides de design.

Usage : python tools/layouts.py
Sortie : tools/catalog/layouts.json + tools/catalog/layouts.md
Images : python tools/render.py layouts  (masques annotés + slides de design)
"""
import json
from pathlib import Path

from common import TEMPLATE, emu_in, open_prs

OUT = Path(__file__).parent / "catalog"

# Rôle métier de chaque zone, déduit de sa taille/position (aide au plan)
def role(ph, layout_name):
    t = str(ph.placeholder_format.type).split(" ")[0]
    w, h, top = emu_in(ph.width), emu_in(ph.height), emu_in(ph.top)
    idx = ph.placeholder_format.idx
    if idx == 13:
        return "capsule"
    if "SLIDE_NUMBER" in t:
        return "numero_slide"
    if "TITLE" in t:
        return "titre"
    if abs(w - h) < 0.05 and w <= 2.0:
        return "pastille/cercle (numero ou icone)"
    if h <= 0.9 and w < 11:
        return "sous-titre de colonne"
    if h <= 0.95 and w >= 11:
        return "sous-titre"
    return "contenu"


def main():
    prs = open_prs(TEMPLATE)
    layouts = []
    for li, lay in enumerate(prs.slide_layouts):
        zones = []
        for ph in sorted(lay.placeholders, key=lambda p: (round(emu_in(p.top), 1), emu_in(p.left))):
            zones.append({
                "idx": ph.placeholder_format.idx,
                "type": str(ph.placeholder_format.type).split(" ")[0],
                "role": role(ph, lay.name),
                "left": emu_in(ph.left), "top": emu_in(ph.top),
                "width": emu_in(ph.width), "height": emu_in(ph.height),
            })
        n_cols = sum(1 for z in zones if z["role"].startswith("pastille"))
        # Ordre VISUEL des éléments (gauche->droite, haut->bas) : les idx ne suivent PAS cet ordre
        elements = []
        pastilles = sorted([z for z in zones if z["role"].startswith("pastille")],
                           key=lambda z: (round(z["top"] / 1.2), z["left"]))
        # chaque zone texte est rattachée à la pastille la plus proche (au-dessus / à gauche d'elle)
        owner = {}
        for z in zones:
            if z["role"] not in ("sous-titre de colonne", "contenu") or z["width"] > 7:
                continue
            cands = [(z["top"] - pz["top"] + abs(z["left"] - pz["left"]), pz["idx"]) for pz in pastilles
                     if z["top"] >= pz["top"] - 0.15 and z["left"] >= pz["left"] - 0.8]
            if cands:
                owner.setdefault(min(cands)[1], []).append(z)
        for pz in pastilles:
            col = sorted(owner.get(pz["idx"], []), key=lambda z: (z["top"], z["left"]))
            elements.append([pz["idx"]] + [z["idx"] for z in col])
        layouts.append({"index": li, "name": lay.name.strip(), "zones": zones,
                        "nb_elements_paralleles": n_cols or None,
                        "ordre_visuel": elements or None})
    # slides de design du template (une par masque + variantes, ex. bureaux FR / EN)
    from pptxops import design_catalog
    designs = []
    for d in design_catalog(prs.slides):
        lay_idx = {ph.placeholder_format.idx for ph in d["slide"].slide_layout.placeholders}
        extra = [sh.name for sh in d["slide"].shapes
                 if not sh.is_placeholder or sh.placeholder_format.idx not in lay_idx]
        designs.append({"n": d["n"], "layout": d["layout"], "lang": d["lang"],
                        "elements_design": len(extra),
                        "apercu_texte": [t[:40] for t in d["texts"]][:6]})
    OUT.mkdir(exist_ok=True)
    (OUT / "layouts.json").write_text(json.dumps({"layouts": layouts, "designs": designs},
                                                 ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# Template de référence — `{TEMPLATE.name}`", "",
          f"{len(layouts)} masques · {len(designs)} slides de design · format 13.33 x 7.5 in.", "",
          "Zones communes : `idx 0` = titre, `idx 13` = capsule (bandeau d'en-tête), numéro de slide.",
          "Images : `catalog/layouts/` (zones annotées) et `catalog/designs/` (slides de design).", "",
          "## Slides de design (toute nouvelle slide part de la slide de design de son masque)", "",
          "| n° | masque | langue | éléments de design en plus du masque | aperçu |", "|---|---|---|---|---|"]
    for d in designs:
        md.append(f"| {d['n']} | {d['layout']} | {d['lang'] or ''} | {d['elements_design']} | "
                  f"{' / '.join(d['apercu_texte'][:4])} |")
    md += ["", "Réutiliser une slide de design AVEC son contenu : `\"mode\": \"design\"` + "
           "`\"design\": \"bureaux_fr\"` / `\"bureaux_en\"` / n° ci-dessus.", "", "## Masques", ""]
    for l in layouts:
        md.append(f"### [{l['index']}] {l['name']}")
        if l["nb_elements_paralleles"]:
            md.append(f"*Éléments parallèles : **{l['nb_elements_paralleles']}***")
        if l.get("ordre_visuel"):
            md.append("")
            md.append("**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :")
            md.append("")
            for k, e in enumerate(l["ordre_visuel"], 1):
                md.append(f"{k}. idx {e}")
        md.append("")
        md.append("| idx | rôle | pos (in) | taille (in) |")
        md.append("|---|---|---|---|")
        for z in l["zones"]:
            md.append(f"| {z['idx']} | {z['role']} | {z['left']}, {z['top']} | {z['width']} x {z['height']} |")
        md.append("")
    (OUT / "layouts.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(layouts)} masques · {len(designs)} slides de design -> {OUT / 'layouts.md'}")


if __name__ == "__main__":
    main()
