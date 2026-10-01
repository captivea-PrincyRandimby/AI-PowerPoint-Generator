# Projet — Transformation des PPT Captivea (charte 2026)

Refaire les anciennes présentations Captivea à la **nouvelle charte 2026** (contenu fidèle, design refait),
puis produire la **version EN** de chaque document FR validé (texte seul, design intact).
Vue d'ensemble des fichiers : `README.md`.

- Tâche 1 → skill `/transformation-fr` (règles complètes : `00. Prompts/01 - Transformation FR - nouvelle charte.md`)
- Tâche 2 → skill `/traduction-en` (règles complètes : `00. Prompts/02 - Traduction EN des documents FR validés.md`)
- Les **prompts 00 font foi** ; ce fichier et les skills n'en sont que la mise en œuvre outillée.

## Dossiers
| Dossier | Rôle |
|---|---|
| `00. Prompts` | Consignes de référence 01 (FR) et 02 (EN) |
| `01. Template` | `2026-template-captivea.potx` = **seule** référence de mise en forme (28 masques + 29 slides de design) |
| `02. French PPT to transform` | Sources à transformer (lecture seule) — à déposer |
| `03. English PPT for translation` | Anciens EN = référence de **wording** uniquement (lecture seule) — à déposer |
| `04. Render from claude` | **Sorties** (arborescence miroir) + `unique_slides(_EN)/` + Excel de suivi — créé par les scripts |
| `05. Render corrected` | Versions **validées par François** → base de la traduction et des slides uniques. Priorité 05 > 04. |
| `tools/` | Scripts Python · `tools/catalog/` = catalogue du template · `tools/exemples/` = plans validés |
| `work/` | Fichiers de travail par document (inventaire, plan, audit, PNG) — régénérables, jamais livrés |

## Règles non négociables
- **Ne jamais écraser** un fichier de `04`/`05` (les scripts refusent). Ne jamais modifier `02`, `03`, `05`.
- **Aucun rendu dans `04` sans validation du plan par l'utilisateur** (autonomie 3 : on valide les choix structurants).
- Nommage `XX - Nom du document` (`FR`/`EN`), même nom FR/EN, arborescence miroir.
- Charte : rouge `#BA131A`, secondaire `#CD5358`, dégradé `BA131A → E2575D`, police **Aptos** (titres Aptos Display).
  Jamais `#BA131A` en aplat de fond. Anciens violets `714B67/7B435D/724D67` (et le violet Office `7030A0` des mots mis en valeur) → `CD5358`.
- Texte **verbatim** (casse, ponctuation, format des nombres). Seule invention permise : le libellé court de la capsule (idx 13).
- **Titre ≠ capsule.** Masque au **nombre exact** d'éléments parallèles (3 items → masque à 3).
- Diagrammes / tableaux **jamais aplatis** (transplant 5a, redessin 5b, tableau identique 5d).
- Pas d'illustrations Freepik/Storyset/amico. Slides masquées remasquées. Notes et commentaires conservés.
- Sommaire (`Summary`) obligatoire juste après la couverture dès qu'il y a des sections.

## Chaîne outillée (lancer depuis la racine du projet)
```
python tools/todo.py                                  # état : template, dossiers, reste à faire FR / EN
python tools/inventory.py "<source>"                  # -> work/<doc>/inventory.md (+ .json)
python tools/render.py png "<source>"                 # -> PNG + planche de la source (via PowerPoint)
python tools/tracking.py find "<source>"              # slides déjà présentes dans unique_slides
python tools/build.py init "<source>"                 # -> work/<doc>/plan.json (squelette)
   … Claude complète le plan → VALIDATION UTILISATEUR …
python tools/build.py run "work/<doc>/plan.json"      # -> 04/<miroir>/<nom>.pptx (+ recharte auto)
python tools/audit.py "<rendu 04>"                    # gate QA : 0 erreur exigée
python tools/render.py compare "<rendu 04>"           # source ↔ rendu côte à côte, à regarder
python tools/tracking.py sync "<rendu 04>"            # lignes « Réutilisation » dans l'Excel
```
Traduction : `translate.py export` (pré-rempli : glossaire, template, mémoire) → Claude complète
`work/<doc>/translate.json` → `translate.py apply` → `audit.py --en` → `translate.py memoriser`.
Template modifié : `python tools/layouts.py` puis `python tools/render.py layouts` (régénère `tools/catalog/`).

## Le template et ses slides de design (tools/catalog/layouts.md + layouts/ + designs/)
- **Slides de design** = slides d'exemple du `.potx` (une par masque + « Nos bureaux » FR n° 28 / EN n° 29).
  `build.py` crée chaque nouvelle slide en **clonant la slide de design de son masque** puis en la vidant de ses
  textes d'exemple (et des zones orphelines) : tout élément graphique ajouté au template est repris automatiquement.
- **Nos bureaux** → `"mode": "design", "design": "bureaux_fr"` (ou `bureaux_en`) : design ET contenu officiels du template
  (liste de bureaux à jour, dont Suisse / Genève). À la traduction, la slide FR est remplacée par la jumelle EN du template.
- `idx 0` = titre, `idx 13` = capsule. `Standard - Title only - Wide` : titre déporté à droite → place pour un grand visuel.
- ⚠ Les **idx ne suivent pas l'ordre visuel**. Ex. `Circles - 3 columns` gauche→droite = 23 / 20 / 26 ;
  `Circles - 4 columns` = 23 / 29 / 32 / 26 ; `Boxed - 3 columns` = 14 / 20 / 17. Toujours vérifier « Ordre visuel » dans le catalogue.
- `1_Main Title` (couverture) : titre idx 0, sous-titre idx 1 (pas de capsule).
- `Section Title` : titre idx 0, capsule idx 13, **numéro de section dans idx 1** (le template n'a pas de cercle de numéro).
- `Summary` : numéros 14,18,22,26,30 (col. gauche) puis 16,20,24,28,32 ; libellé = idx + 1 (rempli automatiquement par `mode: summary`).
- `Standard - 3 columns` : 3 colonnes de texte (titres 15 / 19 / 17, textes 16 / 20 / 18 de gauche à droite).
- Les noms de masques sont distincts même s'ils se ressemblent (`Circles - 2 columns X2` ≠ `3_Circles - 2 columns X2`) : les écrire exactement.

## Pièges connus
- État masqué = attribut `show="0"` sur `<p:sld>` de chaque slide (pas dans presentation.xml) — géré par les scripts.
- `.potx` : converti automatiquement en `.pptx` dans `work/_cache/` (template et sources).
- python-pptx : on ajoute les slides AVANT de supprimer celles du template, et on supprime par objet — géré par `build.py`.
- Aptos est plus large que les anciennes polices : vérifier les retours à la ligne dans les SmartArt et les transplants (ex. « Odo/o »).
- Traduction : un même fragment FR peut changer de sens selon la slide (libellé coupé en 2 lignes dont l'ordre s'inverse en EN,
  ex. « ANALYSE / D’IMPLÉMENTATION » → « IMPLEMENTATION / ANALYSIS ») → ces cas sont dans `memoire_traduction.json` (« ambigus »)
  et proposés en `suggestions`, jamais appliqués automatiquement.
- Alignement FR ↔ ancien EN (03) : l'ancien EN n'a pas toujours le même contenu à la même position
  (slides USA au lieu de France, colonnes réordonnées, notes différentes) → n'accepter une formulation que si les chiffres
  sont identiques et le sens correct, vérifier les noms propres (AvaTax, Gantt…). Les tarifs restent ceux du FR.
- Gros decks répétitifs (ex. ERP Upgrade) : écrire un générateur de plan sur le modèle de `tools/exemples/gen_plan_erp_upgrade.py`
  (fiches « features », intercalaires, réutilisation des slides identiques au deck ERP).
- Icônes SVG blanches (classes `MsftOfcThm_*`) : recolorées au rouge charte par `"recolor"` ; images PNG blanches (logos
  partenaires) invisibles sur fond blanc → les signaler plutôt que les poser telles quelles.
- ⚠ Thème du template : la couleur `accent6` vaut encore `714B67` (ancien violet). Toute forme copiée qui utilise
  accent6 (ex. post-it « Should be checked… », souvent via son style) devient violette → `recharte` la passe en `CD5358`,
  l'audit la signale.
- Chiffre clé dans un cercle porté par l'ancien masque (ex. pastille « 57h / 7410€ ») : copié seul, c'est un texte blanc
  sans fond → invisible. Le poser avec `"place": [{…, "badge": true}]` (cercle au dégradé charte).
- Document déjà corrigé par François sur un ancien template 2026 (05 de l'ancien projet, mêmes noms de masques et
  mêmes idx) : partir de ce 05 (validé) et non de la source brute. Slides de contenu en `"mode": "clone"` (posées
  sur le masque du même nom, mise en forme conservée, `zones` pour corriger une capsule) ; couverture, sommaire et
  sections refaits (le numéro de section du 05 était en idx 15).
- La slide validée peut contenir des résidus (ex. Trebuchet MS Bold) : l'audit les détecte, `recharte` les corrige.
- Point ouvert hérité : chiffres « One software, one success story » (+16M/+7K/+70K deck ERP vs +15M/+6K/+50K MMB et Upgrade) → à trancher.
