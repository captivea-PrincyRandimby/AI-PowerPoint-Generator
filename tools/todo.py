"""État du projet : template utilisé, sources FR sans rendu, FR validés sans version EN.

Usage : python tools/todo.py
"""
import re

from common import CORRECTED, PPT_EXT, REF_EN, RENDER, SRC_FR, TEMPLATE, TEMPLATE_DIR


def docs(base):
    if not base.exists():
        return []
    return sorted(p for p in base.rglob("*") if p.suffix.lower() in PPT_EXT
                  and not p.name.startswith("~$") and "unique_slides" not in str(p))


def main():
    print(f"Template : {TEMPLATE.relative_to(TEMPLATE_DIR.parent) if TEMPLATE.exists() else 'INTROUVABLE'}")
    for d in (SRC_FR, REF_EN, RENDER, CORRECTED):
        print(f"  {'✅' if d.exists() else '—'} {d.name}{'' if d.exists() else '  (absent : à créer / déposer)'}")
    print("\n== Tâche 1 — Transformation FR (02 -> 04) ==")
    srcs = docs(SRC_FR)
    if not srcs:
        print("  (aucune source : déposer les PPT à transformer dans « 02. French PPT to transform »)")
    for src in srcs:
        rel = src.relative_to(SRC_FR)
        out = RENDER / rel.parent / (rel.stem + ".pptx")
        state = "✅ rendu présent" if out.exists() else "⏳ à faire"
        validated = (CORRECTED / rel.parent / (rel.stem + ".pptx")).exists()
        print(f"  {state:16} {'· validé 05' if validated else '':11} {rel}")
    print("\n== Tâche 2 — Traduction EN (05 FR -> 04 EN) ==")
    fr_docs = [p for p in docs(CORRECTED) if not p.stem.upper().startswith("EN")]
    if not fr_docs:
        print("  (aucun document FR validé dans « 05. Render corrected »)")
    for fr in fr_docs:
        rel = fr.relative_to(CORRECTED)
        en_name = re.sub(r"^FR(\s*-)", r"EN\1", rel.stem)
        out = RENDER / rel.parent / (en_name + ".pptx")
        print(f"  {'✅ EN présent' if out.exists() else '⏳ à traduire':16} {rel}")


if __name__ == "__main__":
    main()
