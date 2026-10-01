"""Inventaire détaillé d'un PPT source (base du plan de transformation).

Usage : python tools/inventory.py "<chemin du .pptx/.potx>"
Sortie : work/<doc>/inventory.json + inventory.md

Pour chaque slide : état masqué, masque source, textes (y compris dans les groupes),
tableaux, images (dont illustrations Freepik/Storyset/amico), SmartArt, graphiques,
groupes / diagrammes faits main, polices et couleurs utilisées, notes, commentaires,
et des indices de classement (section ? nb d'éléments parallèles ?).
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from common import (A, ALLOWED_FONTS, is_group, is_picture, is_textbox, OLD_VIOLETS, emu_in, is_hidden, iter_shapes, norm,
                    notes_text, open_prs, work_dir)

ILLUSTRATION_MARKERS = re.compile(rb"freepik|storyset|amico|stories|pana|rafiki|bro\b", re.I)
DGM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
CHART_URI = "http://schemas.openxmlformats.org/drawingml/2006/chart"


def comments_of(slide):
    out = []
    for rel in slide.part.rels.values():
        if rel.reltype.endswith("/comments"):  # anciens et modernes commentaires
            try:
                blob = rel.target_part.blob.decode("utf-8", "ignore")
                out += [norm(t) for t in re.findall(r"<(?:p:)?text>(.*?)</(?:p:)?text>", blob, re.S)]
                out += [norm(re.sub("<[^>]+>", " ", t))
                        for t in re.findall(r"<a:p>(.*?)</a:p>", blob, re.S)]
            except Exception:
                pass
    return [c for c in out if c]


def picture_info(sh):
    info = {"name": sh.name, "left": emu_in(sh.left), "top": emu_in(sh.top),
            "width": emu_in(sh.width), "height": emu_in(sh.height)}
    try:
        img = sh.image
        blob = img.blob
        info["format"] = img.ext
        info["sha1"] = hashlib.sha1(blob).hexdigest()[:12]
        info["illustration_freepik"] = bool(ILLUSTRATION_MARKERS.search(blob[:200000])) \
            if img.ext in ("svg", "emf", "wmf") else False
        # images SVG liées (PowerPoint stocke souvent un PNG + un SVG)
        for el in sh._element.iter("{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip"):
            rid = el.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
            if rid:
                svg = sh.part.related_part(rid).blob
                info["svg"] = True
                if ILLUSTRATION_MARKERS.search(svg):
                    info["illustration_freepik"] = True
        info["px"] = list(img.size)
    except Exception as e:
        info["error"] = str(e)
    return info


def colors_fonts(el):
    colors = Counter(c.get("val").upper() for c in el.iter(A + "srgbClr"))
    fonts = Counter()
    for tag in ("latin", "ea", "cs"):
        for f in el.iter(A + tag):
            tf = f.get("typeface")
            if tf:
                fonts[tf] += 1
    grads = sum(1 for _ in el.iter(A + "gradFill"))
    return colors, fonts, grads


def analyse_slide(i, slide):
    s = {"n": i, "hidden": is_hidden(slide), "layout_source": slide.slide_layout.name,
         "title": None, "texts": [], "tables": [], "pictures": [], "smartart": 0, "charts": 0,
         "groups": [], "connectors": 0, "autoshapes_with_text": 0, "textboxes": 0}
    for sh, depth, path in iter_shapes(slide.shapes):
        if sh.is_placeholder and sh.placeholder_format.type is not None \
                and str(sh.placeholder_format.type).split(" ")[0] in ("TITLE", "CENTER_TITLE") \
                and sh.has_text_frame:
            s["title"] = norm(sh.text_frame.text) or s["title"]
        if is_group(sh):
            n_child = len(sh.shapes)
            s["groups"].append({"path": path, "enfants": n_child,
                                "size": [emu_in(sh.width), emu_in(sh.height)]})
        if is_picture(sh):
            s["pictures"].append(picture_info(sh))
        if sh._element.tag.endswith("}cxnSp"):
            s["connectors"] += 1
        if sh._element.tag.endswith("}graphicFrame"):
            uri = sh._element.find(".//" + A + "graphicData")
            uri = uri.get("uri") if uri is not None else ""
            if uri == DGM_URI:
                s["smartart"] += 1
                # texte du SmartArt (dans la partie data)
                for rel in slide.part.rels.values():
                    if rel.reltype.endswith("/diagramData"):
                        blob = rel.target_part.blob.decode("utf-8", "ignore")
                        for t in re.findall(r"<a:t>(.*?)</a:t>", blob, re.S):
                            if norm(t):
                                s["texts"].append({"shape": path + " [SmartArt]", "depth": depth,
                                                   "text": norm(t)})
            elif uri == CHART_URI:
                s["charts"] += 1
        if getattr(sh, "has_table", False) and sh.has_table:
            tbl = sh.table
            s["tables"].append({"path": path, "rows": len(tbl.rows), "cols": len(tbl.columns),
                                "cells": [[norm(c.text) for c in r.cells] for r in tbl.rows]})
        if sh.has_text_frame and norm(sh.text_frame.text):
            kind = "placeholder" if sh.is_placeholder else ("textbox" if is_textbox(sh) else "forme")
            if kind == "textbox":
                s["textboxes"] += 1
            elif not sh.is_placeholder:
                s["autoshapes_with_text"] += 1
            paras = [norm(p.text) for p in sh.text_frame.paragraphs if norm(p.text)]
            s["texts"].append({"shape": path, "kind": kind, "depth": depth,
                               "ph_idx": sh.placeholder_format.idx if sh.is_placeholder else None,
                               "pos": [emu_in(sh.left), emu_in(sh.top), emu_in(sh.width), emu_in(sh.height)],
                               "paragraphs": paras})
    colors, fonts, grads = colors_fonts(slide._element)
    s["colors"] = dict(colors.most_common(12))
    s["fonts"] = dict(fonts)
    s["old_violets"] = sorted(set(colors) & OLD_VIOLETS)
    s["old_fonts"] = sorted(set(fonts) - ALLOWED_FONTS)
    s["gradients"] = grads
    s["notes"] = notes_text(slide)
    s["comments"] = comments_of(slide)

    # ---- indices de classement (le choix final reste humain / Claude) ----
    hints = []
    all_text = [t for t in s["texts"] if "paragraphs" in t]
    n_words = sum(len(" ".join(t["paragraphs"]).split()) for t in all_text)
    simple = not (s["smartart"] or s["tables"] or s["groups"] or s["charts"])
    if re.search(r"section|intercalaire|divider|titre de section", s["layout_source"], re.I) \
            or (simple and n_words <= 12 and len(all_text) <= 3):
        hints.append("SECTION probable")
    if s["smartart"]:
        hints.append("SmartArt -> 5a")
    if s["tables"]:
        hints.append("Tableau -> 5d (identique)")
    if s["groups"] or s["connectors"] or s["autoshapes_with_text"] >= 3:
        hints.append("Diagramme fait main probable -> 5a/5b (ne pas aplatir)")
    if any(p.get("illustration_freepik") for p in s["pictures"]):
        hints.append("Illustration Freepik/amico -> NE PAS réimporter")
    # éléments parallèles : formes de texte non-placeholder de taille proche, alignées
    boxes = [t for t in all_text if t["kind"] != "placeholder" and t["depth"] <= 1]
    if len(boxes) >= 2:
        sizes = Counter((round(t["pos"][2], 0), round(t["pos"][3], 0)) for t in boxes)
        (sz, cnt) = sizes.most_common(1)[0]
        if 2 <= cnt <= 8:
            hints.append(f"{cnt} éléments parallèles possibles (taille ~{sz[0]}x{sz[1]} in) -> masque à {cnt} ?")
    if s["hidden"]:
        hints.append("MASQUÉE -> remasquer")
    s["hints"] = hints
    return s


def to_md(doc, slides):
    md = [f"# Inventaire — {doc.name}", "",
          f"{len(slides)} slides · masquées : {[s['n'] for s in slides if s['hidden']] or 'aucune'}", "",
          "| # | masquée | titre | masque source | contenu | indices |", "|---|---|---|---|---|---|"]
    for s in slides:
        content = []
        if s["tables"]: content.append(f"{len(s['tables'])} tableau(x)")
        if s["smartart"]: content.append(f"{s['smartart']} SmartArt")
        if s["charts"]: content.append(f"{s['charts']} graphique(s)")
        if s["groups"]: content.append(f"{len(s['groups'])} groupe(s)")
        if s["pictures"]: content.append(f"{len(s['pictures'])} image(s)")
        content.append(f"{len(s['texts'])} bloc(s) texte")
        md.append(f"| {s['n']} | {'oui' if s['hidden'] else ''} | {(s['title'] or '')[:60]} | "
                  f"{s['layout_source']} | {', '.join(content)} | {'; '.join(s['hints'])} |")
    md.append("")
    for s in slides:
        md.append(f"## Slide {s['n']}{' (MASQUÉE)' if s['hidden'] else ''} — {s['title'] or '(sans titre)'}")
        md.append(f"Masque source : `{s['layout_source']}`")
        if s["hints"]: md.append("Indices : " + " · ".join(s["hints"]))
        for t in s["texts"]:
            if "paragraphs" in t:
                ind = "  " * t["depth"]
                md.append(f"- {ind}**{t['shape']}** ({t['kind']}, pos {t['pos']}) : " + " ¶ ".join(t["paragraphs"]))
            else:
                md.append(f"- **{t['shape']}** : {t['text']}")
        for tb in s["tables"]:
            md.append(f"- Tableau {tb['rows']}x{tb['cols']} :")
            for r in tb["cells"]:
                md.append("  | " + " | ".join(c or " " for c in r) + " |")
        for p in s["pictures"]:
            flag = " ⚠ ILLUSTRATION FREEPIK" if p.get("illustration_freepik") else ""
            md.append(f"- Image `{p['name']}` {p.get('format','')} {p['width']}x{p['height']} in{flag}")
        if s["old_fonts"] or s["old_violets"]:
            md.append(f"- Ancienne charte : polices {s['old_fonts']} · violets {s['old_violets']}")
        if s["notes"]: md.append(f"- **Notes** : {norm(s['notes'])[:500]}")
        if s["comments"]: md.append(f"- **Commentaires** : {s['comments']}")
        md.append("")
    return "\n".join(md)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    doc = Path(sys.argv[1]).resolve()
    prs = open_prs(doc)
    slides = [analyse_slide(i, s) for i, s in enumerate(prs.slides, 1)]
    out = work_dir(doc)
    (out / "inventory.json").write_text(json.dumps({"document": str(doc), "slides": slides},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "inventory.md").write_text(to_md(doc, slides), encoding="utf-8")
    print(f"{len(slides)} slides · masquées : {[s['n'] for s in slides if s['hidden']]}")
    print(f"-> {out / 'inventory.md'}")


if __name__ == "__main__":
    main()
