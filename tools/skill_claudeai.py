"""Empaquette le projet en skill claude.ai (zip à importer dans Customize > Skills > Upload a skill).

Usage : python tools/skill_claudeai.py [--out <chemin du zip>]
        (par défaut : captivea-ppt.zip à côté du dossier PROJECT)

Dans claude.ai, l'utilisateur joint simplement ses decks dans la conversation et récupère le .pptx au
nouveau design : pas de dossiers 02-05, les scripts travaillent dans un dossier temporaire
(variable CAPTIVEA_WORK) et lisent les fichiers joints là où ils sont.

Contenu du zip (dossier racine captivea-ppt/) : SKILL.md (ci-dessous), reference/regles.md (sections
« règles / template / pièges » de CLAUDE.md), 00. Prompts, 01. Template, tools/ (scripts, catalogue,
plans d'exemple, glossaire, mémoire de traduction). Les outils propres au projet (dossiers, Excel de
suivi, catalogue) ne sont pas repris.
À relancer après chaque changement de règles, de plans ou de mémoire de traduction, puis réimporter.
"""
import argparse
import re
import zipfile
from pathlib import Path

from common import ROOT

NAME = "captivea-ppt"

SKILL_MD = """---
name: captivea-ppt
description: Version claude.ai (navigateur). À partir d'un deck PowerPoint Captivea joint à la conversation, produire le fichier au nouveau design charte 2026 (template 2026-template-captivea.potx), ou sa traduction anglaise. Utiliser dès que l'utilisateur joint un deck Captivea à transformer, refaire, recharter ou traduire.
---

# Captivea PPT — nouveau design 2026 (claude.ai)

L'utilisateur joint simplement ses fichiers dans la conversation et récupère le .pptx au nouveau design.
**Aucun dossier à créer ni à demander** : tout se passe dans un dossier de travail temporaire et le
fichier produit est donné en téléchargement.
(Dans Claude Code avec le dossier PROJECT ouvert, ne pas utiliser ce skill : `/transformation-fr`, `/traduction-en`.)

## Mise en route (à chaque conversation, sans en parler à l'utilisateur)
- `SKILL` = le dossier de ce skill. Il est en lecture seule : ne rien y écrire.
- Lancer chaque commande avec `CAPTIVEA_WORK=/tmp/captivea` (inventaires, plans, journaux, images y vont) :
  `CAPTIVEA_WORK=/tmp/captivea python $SKILL/tools/<script>.py …`
- Entrées = les fichiers joints, là où ils sont. Sortie = le dossier des fichiers à télécharger de la
  conversation (ex. `/mnt/user-data/outputs/`), avec le nom de la source (`FR - …` / `EN - …`, en `.pptx`).
- Si un module manque (python-pptx, lxml, Pillow) : `pip install` ; sinon le signaler.

## Identifier ce qui est joint
- Un deck FR à transformer (cas courant).
- La version déjà corrigée par François (même nom, souvent faite sur un ancien template 2026) : si elle
  existe, c'est elle la base.
- Un deck FR validé (+ éventuellement l'ancien deck EN) à traduire.
Deux fichiers de même nom : les distinguer par leur contenu (nombre de slides, sommaire) plutôt que demander.

## Transformer un deck au nouveau design
1. **Plan déjà existant ?** Chercher le document ci-dessous. S'il y est, exécuter son plan tel quel : c'est
   le plan produit et contrôlé dans Claude Code, le résultat sera identique. Ne refaire des choix que si
   l'utilisateur le demande.

   | Document (nom du fichier joint) | Plan | Fichiers nécessaires |
   |---|---|---|
   | … ERP Integration Offer | `tools/exemples/plan_erp_integration.json` | le deck |
   | … Update Odoo version (ERP Upgrade) | `tools/exemples/gen_plan_erp_upgrade.py <deck> <deck ERP Integration> <ERP Integration au nouveau design>` | + deck ERP Integration et sa version au nouveau design (la produire d'abord dans la conversation) |
   | … MMB Market | `tools/exemples/gen_plan_mmb_market.py <deck>` | le deck |
   | … Template Analysis V4.1 | `tools/exemples/gen_plan_template_analysis.py <deck>` | le deck |
   | … AI Agents Offer | `tools/exemples/gen_plan_ai_agents_offer.py <version de François>` | la version corrigée par François (26 slides) ; si seule la source brute est jointe, demander la version de François |

   Un générateur (`.py`) écrit le plan et affiche son chemin ; un plan `.json` s'utilise directement.
2. **Sinon, écrire le plan.**
   - `inventory.py <deck>` puis lire l'inventaire (chemin affiché).
   - `render.py png <deck>` et regarder la planche.
   - Consulter `tools/catalog/layouts.md` et ses images.
   - `build.py init <deck>` puis compléter le plan selon `reference/regles.md` et
     `00. Prompts/01 - Transformation FR - nouvelle charte.md` (ils font foi). Format du plan : en tête de
     `tools/build.py` ; exemples : `tools/exemples/`.
   - Si François a déjà corrigé ce deck, partir de sa version (clone sur le masque du même nom, voir regles.md).
3. **Construire** : `build.py run <plan.json> --source <fichier joint de base> --out <sortie>/<nom>.pptx`
4. **Contrôler.**
   - `audit.py <sortie>` : 0 erreur exigée. Sinon corriger le plan, supprimer la sortie, reconstruire.
   - `render.py png <sortie>` et regarder les slides. Le rendu passe par LibreOffice : il est approximatif
     (police Aptos remplacée), le préciser si un doute visuel reste.
5. **Livrer** le .pptx en téléchargement avec un court récapitulatif : structure, choix faits,
   avertissements de l'audit, points à faire vérifier par François. Ne pas attendre de validation avant de
   générer ; pour une retouche demandée ensuite : corriger le plan, supprimer l'ancienne sortie, reconstruire.

## Traduire un deck validé en anglais
1. `translate.py export <deck FR> [--ref <ancien deck EN joint>]` : écrit `translate.json` (chemin affiché),
   pré-rempli avec le glossaire, le template et la mémoire de traduction.
2. Compléter les entrées vides selon `00. Prompts/02 - Traduction EN des documents FR validés.md`. Les
   « suggestions » sont à trancher, jamais appliquées d'office.
3. `translate.py apply <deck FR> --out <sortie>/EN - <nom>.pptx`, puis `audit.py <sortie EN> --en <deck FR>`
   et vérifier le rendu.
4. Livrer le .pptx EN.

## Règles
`reference/regles.md` (charte, verbatim, masques, pièges connus) et `00. Prompts/` font foi. Dans ces
textes : « 02 » = deck FR joint, « 03 » = ancien deck EN joint, « 05 » = version corrigée par François,
« 04 » = fichier produit. Ignorer ce qui concerne les dossiers du projet, l'Excel de suivi et la validation
préalable du plan.
"""

INCLUDE = ["00. Prompts", "01. Template", "tools"]
EXCLUDE = {"todo.py", "tracking.py", "layouts.py", Path(__file__).name}   # outils propres au projet
RULE_SECTIONS = ("## Règles non négociables", "## Le template et ses slides de design", "## Pièges connus")
PROJECT_ONLY = ("- **Ne jamais écraser**", "- **Aucun rendu dans `04`")


def rules_md():
    """Sections de CLAUDE.md utiles hors du projet (sans les règles liées aux dossiers 04/05)."""
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    parts = re.split(r"(?m)^(?=## )", text)
    keep = [p for p in parts if p.startswith(RULE_SECTIONS)]
    lines = [l for l in "".join(keep).splitlines() if not l.startswith(PROJECT_ONLY)]
    return "# Règles du projet de transformation Captivea\n\n" + "\n".join(lines).strip() + "\n"


def files():
    for item in INCLUDE:
        p = ROOT / item
        for f in ([p] if p.is_file() else sorted(p.rglob("*"))):
            if f.is_file() and "__pycache__" not in f.parts and f.name not in EXCLUDE:
                yield f, f.relative_to(ROOT).as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent / f"{NAME}.zip"))
    out = Path(ap.parse_args().out).resolve()
    n = 2
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{NAME}/SKILL.md", SKILL_MD)
        z.writestr(f"{NAME}/reference/regles.md", rules_md())
        for f, arc in files():
            z.write(f, f"{NAME}/{arc}")
            n += 1
    print(f"{n} fichiers -> {out} ({out.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
