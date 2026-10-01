# Transformation des présentations Captivea — charte 2026

Outil pour refaire les anciennes présentations PowerPoint Captivea dans le **nouveau template 2026**,
puis en produire la **version anglaise**, avec Claude Code et une chaîne de scripts Python.

1. **Transformation FR** : un ancien PPT est recréé dans le template 2026. Le contenu est repris mot pour mot, le design est entièrement refait.
2. **Traduction EN** : un document FR validé est traduit. Seul le texte change, le design reste identique.

---

## Démarrage rapide

1. Ouvrir **ce dossier (`PROJECT/`)** dans VS Code avec Claude Code. `CLAUDE.md` et les skills se chargent alors automatiquement.
2. Installer les dépendances : `pip install -r requirements.txt`. Microsoft PowerPoint doit être installé (Windows), car il sert au rendu en images.
3. Déposer les sources dans `02. French PPT to transform/` et les anciennes versions anglaises dans `03. English PPT for translation/` (voir la structure plus bas).
4. Demander à Claude :
   - `/transformation-fr` → propose le prochain document à transformer, présente le plan pour validation, puis construit et contrôle le rendu ;
   - `/traduction-en` → traduit un document FR validé déposé dans `05. Render corrected/`.
5. État du projet à tout moment : `python tools/todo.py`.

---

## Fichiers du projet et leur rôle

### Consignes et référence

| Fichier | Rôle |
|---|---|
| `00. Prompts/01 - Transformation FR - nouvelle charte.md` | **Règles de référence** de la transformation : fidélité du texte, charte, masques, diagrammes, sommaire, vérifications. Font foi. |
| `00. Prompts/02 - Traduction EN des documents FR validés.md` | **Règles de référence** de la traduction EN : texte seul, wording officiel, données inchangées. Font foi. |
| `01. Template/2026-template-captivea.potx` | **Seul template de référence** (dernière version) : 28 masques et 29 slides de design, dont « Nos bureaux » en FR et en EN. Toute nouvelle slide reprend le design de la slide d'exemple de son masque. |
| `CLAUDE.md` | Mémo lu automatiquement par Claude Code : dossiers, règles non négociables, chaîne d'outils, repères sur le template, pièges connus. |
| `.claude/skills/transformation-fr/SKILL.md` | Déroulé de la transformation FR, lancé avec `/transformation-fr` : analyse, plan, **validation**, construction, contrôle. |
| `.claude/skills/traduction-en/SKILL.md` | Déroulé de la traduction EN, lancé avec `/traduction-en` : export, traduction, **validation**, application, contrôle. |
| `requirements.txt` | Dépendances Python (python-pptx, lxml, openpyxl, pillow, pywin32). |
| `README.md` | Ce fichier. |

### Scripts (`tools/`)

| Script | Rôle |
|---|---|
| `common.py` | Constantes partagées : chemins des dossiers, template de référence, charte (couleurs, polices, dégradé), ouverture des `.potx`, utilitaires. |
| `todo.py` | État du projet : template utilisé, dossiers présents, documents à transformer ou à traduire. |
| `inventory.py` | Analyse d'une source : slides masquées, textes (y compris dans les groupes), tableaux, SmartArt, images, illustrations Freepik, notes, anciennes polices et couleurs, indices de classement. |
| `layouts.py` | Génère le **catalogue du template** : masques, zones, ordre visuel des zones et liste des slides de design. |
| `build.py` | **Construit le PPT** à partir d'un plan JSON (format documenté en tête du fichier). Chaque slide part de la slide de design du template. Modes `fill`, `transplant`, `design`, `reuse`, `clone`, `summary`. |
| `pptxops.py` | Opérations bas niveau : clonage des slides de design, copie de slides et de formes entre fichiers (images, SmartArt, liens), remplissage des zones, icônes, fiches fonctionnalités. |
| `recharte.py` | Mise à la charte automatique : anciens violets, polices hors charte, aplats rouges, anciens dégradés. |
| `audit.py` | **Contrôle qualité bloquant** : texte repris mot pour mot, slides masquées, notes, charte, sommaire, images déformées, texte d'exemple du template oublié, titre identique à la capsule, contrôles EN. |
| `render.py` | Rendu en images via PowerPoint : PNG par slide, planches, comparaison source ↔ rendu, images du catalogue. |
| `translate.py` | Traduction EN : export du texte à traduire (pré-rempli), application sans toucher au design, remplacement de « Nos bureaux » par sa version EN officielle, enrichissement de la mémoire (`memoriser`). |
| `skill_claudeai.py` | Empaquette le projet en **skill claude.ai** : `captivea-ppt.zip` à côté de `PROJECT/`, à importer dans claude.ai (Customize → Skills → Upload a skill). Sans les données 02–05 ni `work/`. |
| `tracking.py` | Bibliothèque des slides récurrentes (`unique_slides`, `unique_slides_EN`) et Excel de suivi (Source / Réutilisation). |
| `glossaire.json` | Terminologie EN imposée (SOMMAIRE → TABLE OF CONTENTS, NOS BUREAUX → OUR OFFICES…). |
| `memoire_traduction.json` | **Mémoire de traduction** FR→EN déjà validée (1 756 paires, issues des decks ERP Integration et ERP Upgrade), plus les textes « ambigus » proposés en suggestions. |
| `catalog/layouts.md` · `catalog/layouts.json` | Catalogue du template : zones de chaque masque, **ordre visuel**, slides de design. |
| `catalog/layouts/*.png` | Chaque masque rendu avec ses numéros de zones (idx). |
| `catalog/designs/*.png` | Les 29 slides de design du template, telles quelles. |
| `exemples/plan_erp_integration.json` | **Plan complet et validé** du deck « Intégration ERP Odoo » (50 slides) : exemple de référence pour écrire un plan. |
| `exemples/gen_plan_erp_upgrade.py` | Exemple de **générateur de plan** pour un gros deck répétitif (ERP Upgrade, 240 slides : fiches nouveautés, intercalaires, réutilisation des slides du deck ERP). |
| `exemples/gen_plan_mmb_market.py` | Exemple de générateur pour un deck déjà en anglais (MMB Market), qui reprend les choix du plan ERP. |

---

## Dossiers de travail (créés ou déposés au fil du projet)

Ces dossiers ne font pas partie de l'outil. Ils sont créés à l'usage, en respectant ces noms exacts :

```
PROJECT/
├── 02. French PPT to transform/     ← à déposer : sources à transformer (lecture seule)
│   └── Sales knowledge/01. ERP Integration Offer/FR - …potx   (sous-dossiers libres)
├── 03. English PPT for translation/ ← à déposer : anciennes versions EN, même arborescence (wording uniquement)
├── 04. Render from claude/          ← créé par les scripts : rendus FR et EN, arborescence miroir de 02
│   ├── unique_slides/ · unique_slides_EN/        (bibliothèque des slides récurrentes)
│   └── Slides uniques - suivi.xlsx · Slides uniques EN - suivi.xlsx
├── 05. Render corrected/            ← à déposer : versions FR corrigées et validées par François (base de l'EN)
└── work/                            ← créé par les scripts : inventaires, plans, audits, PNG (régénérable, jamais livré)
```

- **Nommage** : `FR - Nom du document.pptx` → `EN - Nom du document.pptx`, avec le même nom et la même arborescence.
- **Aucun fichier de `04`/`05` n'est jamais écrasé** : les scripts refusent.
- `work/` peut être supprimé à tout moment ; il se reconstruit.

---

## Chaîne de travail

```
Transformation FR
  todo.py → inventory.py → render.py png → build.py init → [Claude complète le plan]
  → VALIDATION DU PLAN → build.py run → audit.py (0 erreur) → render.py compare → tracking.py sync

Traduction EN (depuis 05. Render corrected)
  translate.py export (pré-rempli : glossaire, template, mémoire) → [Claude complète]
  → VALIDATION → translate.py apply → audit.py --en → render.py png → translate.py memoriser
```

**Version claude.ai** (navigateur, sans installation) : `python tools/skill_claudeai.py` produit `captivea-ppt.zip`. Dans claude.ai : activer l'exécution de code (Paramètres → Capacités), importer le zip (Customize → Skills → + → Upload a skill), puis joindre un deck dans une conversation. Différences : rendu visuel via LibreOffice (approximatif) au lieu de PowerPoint, rien n'est conservé entre conversations (télécharger la mémoire de traduction mise à jour, la remettre dans `tools/` puis refaire le zip).

**Si le template change** (nouvelle version déposée dans `01. Template/`) : lancer `python tools/layouts.py` puis `python tools/render.py layouts` pour régénérer le catalogue. Si le fichier change de nom, mettre à jour `TEMPLATE_NAME` dans `tools/common.py` ; à défaut, le seul `.potx` du dossier est utilisé.
