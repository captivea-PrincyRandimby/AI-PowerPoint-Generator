"""Mise à la charte 2026 du contenu des SLIDES (jamais les masques du template).

Règles appliquées :
  1. anciens violets (714B67, 7B435D, 724D67, 7030A0) et couleur de thème accent6 (= 714B67 dans le
     thème du template) -> CD5358
  2. toute police hors charte (Trebuchet MS, Tahoma, Calibri, Arial…) -> Aptos
  3. aplats rouges #BA131A (ou accent1) en FOND (slide ou forme large) -> dégradé charte
  4. anciens dégradés de fond / de forme -> dégradé charte

Usage CLI : python tools/recharte.py "<fichier 04 .pptx>"   (modifie le fichier de rendu 04)
En module : recharte_prs(prs) -> rapport (utilisé automatiquement par build.py)
"""
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation

from common import (A, ALLOWED_FONTS, OLD_FONTS, OLD_VIOLETS, P, RED, RED2, GRAD_END, RENDER,
                    charte_gradient)

MIN_BG_AREA_IN2 = 1.5          # au-delà : forme considérée comme "fond"
EMU_IN = 914400
CHARTE_STOPS = {RED, GRAD_END}


def _is_red(fill):
    c = fill.find(A + "srgbClr")
    if c is not None and c.get("val", "").upper() == RED:
        return True
    s = fill.find(A + "schemeClr")
    return s is not None and s.get("val") == "accent1"


def _area_in2(sppr):
    ext = sppr.find(f"{A}xfrm/{A}ext")
    if ext is None:
        return None
    return int(ext.get("cx", 0)) * int(ext.get("cy", 0)) / EMU_IN ** 2


def _is_charte_gradient(grad):
    vals = {c.get("val", "").upper() for c in grad.iter(A + "srgbClr")}
    schemes = {c.get("val") for c in grad.iter(A + "schemeClr")}
    if vals:
        return vals <= CHARTE_STOPS | {RED2}
    return bool(schemes) and schemes <= {"accent1", "accent2"}


def _replace(old, new):
    old.getparent().replace(old, new)


def recharte_element(root, report, where):
    # 1. violets
    for c in root.iter(A + "srgbClr"):
        if c.get("val", "").upper() in OLD_VIOLETS:
            report.append(f"{where}: violet {c.get('val')} -> {RED2}")
            c.set("val", RED2)
    # 1 bis. couleur de thème accent6 : dans le thème du template, accent6 = 714B67 (ancien violet)
    for c in list(root.iter(A + "schemeClr")):
        if c.get("val") == "accent6":
            new = etree.Element(A + "srgbClr", val=RED2)
            for child in list(c):
                new.append(child)
            c.getparent().replace(c, new)
            report.append(f"{where}: couleur de thème accent6 (ancien violet) -> {RED2}")
    # 2. polices
    for tag in ("latin", "ea", "cs"):
        for f in root.iter(A + tag):
            if f.get("typeface") and f.get("typeface") not in ALLOWED_FONTS:
                report.append(f"{where}: police {f.get('typeface')} -> Aptos")
                f.set("typeface", "Aptos")
                for k in ("panose", "pitchFamily", "charset"):
                    f.attrib.pop(k, None)
    # 3 & 4. fonds (spPr de formes, bgPr de slide)
    for container_tag in (P + "spPr", P + "bgPr", P + "grpSpPr"):
        for sppr in root.iter(container_tag):
            area = _area_in2(sppr) if container_tag != P + "bgPr" else 999
            for fill in list(sppr):
                if fill.tag == A + "solidFill" and _is_red(fill):
                    if area is None or area >= MIN_BG_AREA_IN2:
                        report.append(f"{where}: aplat rouge de fond -> dégradé")
                        _replace(fill, charte_gradient())
                elif fill.tag == A + "gradFill" and not _is_charte_gradient(fill):
                    report.append(f"{where}: ancien dégradé -> dégradé charte")
                    _replace(fill, charte_gradient())


def recharte_prs(prs, slides=None):
    report = []
    for i, slide in enumerate(prs.slides, 1):
        if slides and i not in slides:
            continue
        recharte_element(slide._element, report, f"slide {i}")
    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = Path(sys.argv[1]).resolve()
    if RENDER.resolve() not in path.parents:
        sys.exit("recharte CLI : uniquement sur un fichier de 04. Render from claude")
    prs = Presentation(str(path))
    rep = recharte_prs(prs)
    prs.save(str(path))
    print("\n".join(rep) or "Rien à corriger.")


if __name__ == "__main__":
    main()
