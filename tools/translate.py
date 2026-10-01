"""Traduction EN d'un document FR validé — TEXTE UNIQUEMENT, design intact.

  python tools/translate.py export "<FR validé 05 .pptx>" [--ref "<ancien EN 03>"]
        -> work/<doc>/translate.json   (1 entrée par paragraphe / cellule / note, champ "en" à remplir)
        -> work/<doc>/ref_en.md        (textes de la référence EN, slide par slide, pour le wording)
  python tools/translate.py apply "<FR validé 05 .pptx>" [--out <chemin>]
        -> 04. Render from claude/<miroir>/EN - <nom>.pptx
  python tools/translate.py memoriser "<FR validé 05 .pptx>"
        -> ajoute les paires FR/EN validées du document à tools/memoire_traduction.json
           (les conflits avec une traduction existante vont dans "ambigus")

Principe : on repart du fichier FR validé et on remplace le texte paragraphe par paragraphe.
- Paragraphe à formatage homogène : le texte EN va dans le 1er run (sa mise en forme est gardée).
- Paragraphe à formatage mixte (ex. un mot en gras) : "runs" liste les morceaux FR ; fournir
  "en_runs" (même nombre d'éléments) pour garder le formatage, sinon "en" est mis dans le 1er run.
- SmartArt : le texte est remplacé à la fois dans les données et dans le dessin mis en cache.
- Pré-remplissage automatique du champ "en" (champ "source" = origine, à RELIRE) :
    1. "glossaire" : terminologie imposée (tools/glossaire.json) ;
    2. "template"  : slides de design du template existant en FR et en EN (ex. « Nos bureaux ») :
                     le wording EN officiel du template est repris ;
    3. "memoire"   : mémoire de traduction validée (tools/memoire_traduction.json).
  Les entrées restées vides sont à traduire (wording de ref_en.md en priorité) ; "suggestions" liste
  les traductions déjà validées ailleurs pour un texte dont le sens dépend du contexte.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from lxml import etree

from common import (A, P, RENDER, REF_EN, TEMPLATE, is_hidden, iter_shapes, norm, notes_text,
                    open_prs, rel_to_source_root, safe_output, set_hidden, set_notes, shape_texts,
                    work_dir)

GLOSSARY = Path(__file__).parent / "glossaire.json"
MEMORY = Path(__file__).parent / "memoire_traduction.json"
DGM_RELS = ("/diagramData", "/diagramDrawing")


def _rpr_key(r):
    rpr = r.find(A + "rPr")
    if rpr is None:
        return ""
    k = etree.tostring(rpr)
    return re.sub(rb' (lang|altLang|dirty|err|noProof)="[^"]*"', b"", k)


def iter_paragraphs(prs):
    """(id, slide_n, lieu, élément a:p) pour chaque paragraphe non vide."""
    for n, slide in enumerate(prs.slides, 1):
        for sh, _, path in iter_shapes(slide.shapes):
            sid = sh.shape_id
            if sh.has_text_frame:
                for k, p in enumerate(sh.text_frame.paragraphs):
                    if norm(p.text):
                        yield f"s{n}/sh{sid}/p{k}", n, path, p._p
            if getattr(sh, "has_table", False) and sh.has_table:
                for ri, row in enumerate(sh.table.rows):
                    for ci, cell in enumerate(row.cells):
                        for k, p in enumerate(cell.text_frame.paragraphs):
                            if norm(p.text):
                                yield f"s{n}/sh{sid}/r{ri}c{ci}/p{k}", n, f"{path} [{ri},{ci}]", p._p
        # SmartArt (partie data)
        for rel in slide.part.rels.values():
            if rel.reltype.endswith("/diagramData"):
                root = etree.fromstring(rel.target_part.blob)
                for k, p in enumerate(root.iter(A + "p")):
                    if norm("".join(t.text or "" for t in p.iter(A + "t"))):
                        yield f"s{n}/dgm{rel.rId}/p{k}", n, "[SmartArt]", p
        if slide.has_notes_slide and norm(notes_text(slide)):
            for k, p in enumerate(slide.notes_slide.notes_text_frame.paragraphs):
                if norm(p.text):
                    yield f"s{n}/notes/p{k}", n, "[notes]", p._p


def runs_of(p):
    return [r for r in p if r.tag == A + "r"]


def para_text(p):
    """Texte d'un paragraphe, les sauts de ligne (a:br) rendus par \\n."""
    out = []
    for c in p:
        if c.tag == A + "r":
            out.append(c.find(A + "t").text or "")
        elif c.tag == A + "br":
            out.append("\n")
    return "".join(out)


def template_twins():
    """Paires FR -> EN issues des slides de design du template disponibles dans les deux langues
    (même masque, une version FR et une version EN, ex. « Nos bureaux »)."""
    from pptxops import design_catalog
    tpl = open_prs(TEMPLATE)
    cat = design_catalog(tpl.slides)
    pairs = {}
    by_layout = {}
    for d in cat:
        if d["lang"]:
            by_layout.setdefault(d["layout"], {})[d["lang"]] = d["slide"]
    for langs in by_layout.values():
        if "fr" not in langs or "en" not in langs:
            continue
        def paras(slide):
            return [para_text(p._p) for sh, _, _ in iter_shapes(slide.shapes) if sh.has_text_frame
                    for p in sh.text_frame.paragraphs if p.text.strip()]
        a, b = paras(langs["fr"]), paras(langs["en"])
        if len(a) == len(b):
            for x, y in zip(a, b):
                pairs.setdefault(norm(x), y)
    return pairs


def cmd_export(fr: Path, ref: Path | None):
    prs = open_prs(fr)
    glossary = json.loads(GLOSSARY.read_text(encoding="utf-8")) if GLOSSARY.exists() else {}
    mem_all = json.loads(MEMORY.read_text(encoding="utf-8")) if MEMORY.exists() else {}
    memory, ambiguous = mem_all.get("paires", {}), mem_all.get("ambigus", {})
    twins = template_twins()
    entries, stats = [], {"glossaire": 0, "template": 0, "memoire": 0, "a_traduire": 0}
    for pid, n, where, p in iter_paragraphs(prs):
        runs = runs_of(p)
        texts = [(r.find(A + "t").text or "") for r in runs]
        fr_txt = para_text(p)
        key = norm(fr_txt)
        e = {"id": pid, "slide": n, "where": where, "fr": fr_txt, "en": ""}
        for origin, table in (("glossaire", glossary), ("template", twins), ("memoire", memory)):
            if table.get(key):
                e["en"], e["source"] = table[key], origin
                stats[origin] += 1
                break
        else:
            stats["a_traduire"] += 1
            if ambiguous.get(key):
                e["suggestions"] = ambiguous[key]   # traduction selon le contexte : à choisir
        if len({_rpr_key(r) for r in runs}) > 1:
            e["runs"] = texts
            e["en_runs"] = []
        entries.append(e)
    wd = work_dir(fr)
    out = wd / "translate.json"
    if out.exists():
        sys.exit(f"Déjà exporté (non écrasé) : {out}")
    out.write_text(json.dumps({"source": str(fr), "entries": entries}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"{len(entries)} paragraphes -> {out}")
    print("Pré-remplis : " + " · ".join(f"{k} {v}" for k, v in stats.items()))
    if ref is None:
        try:
            rel = rel_to_source_root(fr)
        except ValueError:
            rel = Path(fr.name)
        stem = re.sub(r"^FR\s*-?\s*", "", rel.stem)
        cands = [p for p in (REF_EN / rel.parent).glob("*") if p.suffix.lower() in (".pptx", ".potx")] \
            if (REF_EN / rel.parent).exists() else []
        cands.sort(key=lambda p: (stem.lower() not in p.stem.lower(), p.name))
        ref = cands[0] if cands else None
    if ref:
        rprs = open_prs(ref)
        md = [f"# Référence EN — {ref.name}", ""]
        for i, s in enumerate(rprs.slides, 1):
            md.append(f"## Slide {i}")
            md += [f"- {t}" for t in shape_texts(s)]
            if norm(notes_text(s)):
                md.append(f"- *Notes* : {norm(notes_text(s))}")
            md.append("")
        (wd / "ref_en.md").write_text("\n".join(md), encoding="utf-8")
        print(f"Référence EN : {ref.name} -> {wd / 'ref_en.md'}")
    else:
        print("⚠ Aucune référence EN trouvée dans 03 : traduction libre à signaler.")


def set_paragraph(p, en, en_runs=None):
    runs = runs_of(p)
    if not runs:
        return
    if en_runs and len(en_runs) == len(runs):
        for r, t in zip(runs, en_runs):
            r.find(A + "t").text = t
        return
    first = runs[0]
    for r in runs[1:]:
        p.remove(r)
    for br in p.findall(A + "br"):
        p.remove(br)
    segments = en.split("\n")
    first.find(A + "t").text = segments[0]
    anchor = first
    for seg in segments[1:]:
        br = etree.Element(A + "br")
        if first.find(A + "rPr") is not None:
            br.append(etree.fromstring(etree.tostring(first.find(A + "rPr"))))
        anchor.addnext(br)
        nr = etree.fromstring(etree.tostring(first))
        nr.find(A + "t").text = seg
        br.addnext(nr)
        anchor = nr


def design_swaps(prs):
    """Slides du document identiques à une slide de design FR du template qui a une jumelle EN
    (ex. « Nos bureaux ») -> {index: slide de design EN}. Ces slides sont remplacées par la
    version EN officielle du template (mise en page prévue pour l'anglais) au lieu d'être
    traduites sur place."""
    from pptxops import _exact, design_catalog
    tpl = open_prs(TEMPLATE)
    pairs = {}
    for d in design_catalog(tpl.slides):
        if d["lang"]:
            pairs.setdefault(_exact(d["layout"]), {})[d["lang"]] = d
    sig = lambda slide: sorted(norm(sh.text_frame.text) for sh, _, _ in iter_shapes(slide.shapes)
                               if sh.has_text_frame and norm(sh.text_frame.text))
    swaps = {}
    for i, slide in enumerate(prs.slides):
        twin = pairs.get(_exact(slide.slide_layout.name))
        if twin and "fr" in twin and "en" in twin and sig(slide) == sig(twin["fr"]["slide"]):
            swaps[i] = twin["en"]["slide"]
    return swaps, tpl


def cmd_apply(fr: Path, out: str | None):
    from pptxops import PartCopier, clone_slide, delete_slide, move_slide, remove_empty_placeholders
    wd = work_dir(fr)
    data = json.loads((wd / "translate.json").read_text(encoding="utf-8"))
    tr = {e["id"]: e for e in data["entries"]}
    empty = [e["id"] for e in data["entries"] if not (e.get("en") or e.get("en_runs"))]
    if empty:
        sys.exit(f"{len(empty)} entrée(s) sans traduction, ex. {empty[:5]}")
    prs = open_prs(fr)
    swaps, _tpl = design_swaps(prs)       # à repérer AVANT de modifier les textes
    dgm_texts = {}   # slide -> {fr: en} pour propager au dessin SmartArt
    dgm_roots = {}
    for pid, n, where, p in iter_paragraphs(prs):
        e = tr.get(pid)
        if not e:
            continue
        if "/dgm" in pid:
            rid = pid.split("/dgm")[1].split("/")[0]
            dgm_texts.setdefault(n, {})[e["fr"]] = e["en"]
            key = (n, rid)
            if key not in dgm_roots:
                part = prs.slides[n - 1].part.related_part(rid)
                dgm_roots[key] = (part, etree.fromstring(part.blob))
            _, root = dgm_roots[key]
            k = int(pid.rsplit("/p", 1)[1])
            p = list(root.iter(A + "p"))[k]
        set_paragraph(p, e["en"], e.get("en_runs"))
    for (n, rid), (part, root) in dgm_roots.items():
        part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    # dessin SmartArt mis en cache : remplacement par correspondance de texte
    for n, mapping in dgm_texts.items():
        for rel in prs.slides[n - 1].part.rels.values():
            if rel.reltype.endswith("/diagramDrawing"):
                root = etree.fromstring(rel.target_part.blob)
                for p in root.iter(A + "p"):
                    t = para_text(p)
                    if t in mapping:
                        set_paragraph(p, mapping[t])
                rel.target_part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8",
                                                       standalone=True)
    for slide in prs.slides:
        for el in slide._element.iter(A + "rPr", A + "endParaRPr"):
            if el.get("lang", "").startswith("fr"):
                el.set("lang", "en-US")
    # slides de design FR -> jumelle EN officielle du template (position, état masqué, notes conservés)
    copier = PartCopier(prs.part.package)
    for i, en_design in sorted(swaps.items()):
        old_slide = prs.slides[i]
        new_slide = clone_slide(en_design, prs, copier)
        remove_empty_placeholders(new_slide, keep=[0])     # comme au build FR
        set_hidden(new_slide, is_hidden(old_slide))
        set_notes(new_slide, notes_text(old_slide))
        move_slide(prs, new_slide, i)
        delete_slide(prs, old_slide)
        print(f"slide {i + 1} : remplacée par la slide de design EN du template")
    if out:
        target = Path(out)
    else:
        rel = rel_to_source_root(fr)
        name = re.sub(r"^FR(\s*-)", r"EN\1", rel.stem)
        if name == rel.stem:
            name = "EN - " + rel.stem
        target = RENDER / rel.parent / (name + ".pptx")
    safe_output(target)
    prs.save(str(target))
    print(f"-> {target}")


def cmd_memorize(fr: Path):
    data = json.loads((work_dir(fr) / "translate.json").read_text(encoding="utf-8"))
    mem = json.loads(MEMORY.read_text(encoding="utf-8")) if MEMORY.exists() else {"paires": {}, "ambigus": {}}
    pairs, amb = mem.setdefault("paires", {}), mem.setdefault("ambigus", {})
    added = conflicts = 0
    for e in data["entries"]:
        k, en = norm(e["fr"]), (e.get("en") or "").strip()
        if not k or not en or e.get("source") in ("template", "glossaire"):
            continue          # déjà couverts par le template / le glossaire
        if k in amb:
            if en not in amb[k]:
                amb[k].append(en)
        elif k not in pairs:
            pairs[k] = en
            added += 1
        elif pairs[k] != en:
            amb[k] = sorted({pairs.pop(k), en})
            conflicts += 1
    mem["paires"] = dict(sorted(pairs.items()))
    mem["ambigus"] = dict(sorted(amb.items()))
    MEMORY.write_text(json.dumps(mem, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"+{added} paires · {conflicts} conflit(s) -> ambigus · total {len(pairs)} paires")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "apply", "memoriser"])
    ap.add_argument("fr")
    ap.add_argument("--ref")
    ap.add_argument("--out")
    a = ap.parse_args()
    fr = Path(a.fr).resolve()
    if a.cmd == "export":
        cmd_export(fr, Path(a.ref).resolve() if a.ref else None)
    elif a.cmd == "memoriser":
        cmd_memorize(fr)
    else:
        cmd_apply(fr, a.out)


if __name__ == "__main__":
    main()
