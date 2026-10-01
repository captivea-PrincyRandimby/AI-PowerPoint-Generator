---
name: transformation-fr
description: Transformer un ancien PPT Captivea (02. French PPT to transform) à la nouvelle charte 2026 dans 04. Render from claude, avec les slides de design du template 01. Template/2026-template-captivea.potx. Utiliser quand l'utilisateur demande de transformer / recharter / refaire un document, ou de traiter le prochain document "à faire".
argument-hint: "[chemin ou nom du document source]"
---

# Transformation FR — charte 2026

Règles de fond : **lire `00. Prompts/01 - Transformation FR - nouvelle charte.md`** en entier avant de commencer
(réglages de précision en tête du fichier : Fidélité / Rigueur charte / Autonomie). Ce skill décrit l'exécution.

Document ciblé : `$ARGUMENTS` (si vide : lancer `python tools/todo.py` et proposer le premier « à faire »).

Template : `01. Template/2026-template-captivea.potx` (seule référence). Chaque nouvelle slide est créée à partir de
la **slide de design** du template qui utilise son masque (clonée puis vidée de ses textes d'exemple) : le design
des slides du template est donc toujours repris. Catalogue : `tools/catalog/layouts.md`
(masques, zones, **ordre visuel**, slides de design) + images `tools/catalog/layouts/` et `tools/catalog/designs/`.
Si le template a changé : `python tools/layouts.py` puis `python tools/render.py layouts`.

## Étape 1 — Analyse (aucune écriture dans 04)
1. `python tools/inventory.py "<source>"` puis lire `work/<doc>/inventory.md`.
2. `python tools/render.py png "<source>"` puis **regarder** la planche `work/<doc>/png/02 - <nom>/_planche.png`
   et les PNG des slides à diagrammes / tableaux (l'inventaire ne remplace pas l'œil).
3. `python tools/tracking.py find "<source>"` : slides récurrentes déjà dans `unique_slides/` → mode `reuse`.
   Chercher aussi dans `05. Render corrected` (prioritaire) puis `04` une version déjà traitée de la même slide.
4. Consulter `tools/catalog/layouts.md` et les planches du catalogue.

## Étape 2 — Plan (work/<doc>/plan.json)
`python tools/build.py init "<source>"` crée le squelette ; le compléter (format documenté en tête de `tools/build.py`,
exemple complet et validé : `tools/exemples/plan_erp_integration.json` ; pour un gros deck répétitif, écrire un
générateur sur le modèle de `tools/exemples/gen_plan_erp_upgrade.py`). Pour chaque slide source, décider :
- **Couverture** → `1_Main Title` : titre zone 0 (+ sous-titre zone 1 si la source en a un).
- **Section** → `Section Title` : titre 0, capsule 13, **numéro dans la zone 1** ;
  `"section": {"num": "01", "label": "…"}` ; le sommaire (`mode: summary`, juste après la couverture) se remplit seul.
- **Nos bureaux** → `"mode": "design", "design": "bureaux_fr"` (slide de design officielle du template ; `bureaux_en` en anglais).
- **Récurrente** déjà validée (références, chiffres, interlocuteurs, gouvernance, vision, étapes, budget…) → `reuse`.
- **Texte / éléments parallèles** → `fill` dans le masque au **nombre exact** d'éléments ; respecter l'ordre visuel des idx.
- **Diagramme fait main / SmartArt** → `transplant` (5a) dans `Standard - Title only` ou `- Wide`, `box` sous le titre ;
  `exclude` les illustrations Freepik et anciens logos ; `include` les placeholders source qui portent du contenu.
- **Tableau** → `transplant` du tableau (5d, identique) ; **Image** → transplant sans déformation.
- `clone` seulement en dernier recours (slide non représentable), puis recharte automatique.
- Capsule (idx 13) = thème court ; titre = sujet ; jamais identiques. Texte verbatim.

**STOP → présenter le plan à l'utilisateur** sous forme de tableau lisible
(n° source → n° sortie · masque · méthode · capsule / titre · remarques, slides écartées et pourquoi)
et **attendre sa validation** avant tout build. Signaler les choix ambigus (mapping, contenu manquant).

## Étape 3 — Construction & QA (après validation)
1. `python tools/build.py run "work/<doc>/plan.json"` → `04/<miroir>/<nom>.pptx` (recharte inclus).
2. `python tools/audit.py "<rendu>"` → corriger le plan et reconstruire jusqu'à **0 erreur**
   (pour reconstruire : supprimer d'abord le rendu de test que l'on vient de produire soi-même, jamais un fichier validé).
   L'audit signale aussi tout texte d'exemple du template resté en place (« Section Title », « Standard - 1 column »…).
3. `python tools/render.py compare "<rendu>"` → **regarder chaque comparaison** `work/<doc>/compare/NNN.png` :
   chevauchements titre/contenu, vides, texte minuscule, retours à la ligne, diagrammes complets, proportions.
4. `python tools/tracking.py sync "<rendu>"` (lignes Réutilisation). Les nouvelles slides récurrentes seront extraites
   **après validation par François** (`tracking.py extract` depuis `05`).
5. Récapitulatif : fichier produit, slides réutilisées, slides écartées, avertissements d'audit, points à revoir à la main.
