# Prompt 01 — Transformation des PPT français vers la nouvelle charte

## Réglages de précision (ajuster les valeurs entre crochets, 1 = souple → 5 = strict)
- **Fidélité du contenu : [5]** — 1 : adaptation / synthèse libre autorisée · 3 : fidèle, reformulations mineures tolérées · 5 : **verbatim strict** (texte, chiffres, unités, casse), zéro perte, zéro condensation, zéro invention (hors libellé de capsule).
- **Rigueur charte & rendu : [5]** — 1 : l'ancien habillage peut subsister · 3 : recharté avec tolérances · 5 : **100 % nouvelle charte** (dégradés, polices, icônes recolorisées, aucun résidu ancien), slides **remplies harmonieusement**, passe de vérification post-création obligatoire.
- **Autonomie : [3]** — 1 : me demander à chaque doute · 3 : ne demander que sur les **choix structurants** (mapping ambigu, contenu manquant) · 5 : **décider seul** avec valeurs par défaut, ne demander qu'en cas de blocage réel.

## Objectif
Transformer **tous** les fichiers PowerPoint présents dans `02. French PPT to transform` qui ne sont **pas encore** présents dans `04. Render from claude`, en les recréant dans le **nouveau template** et la **nouvelle charte graphique**.

## Dossiers de référence
- **Template** : `01. Template/2026-template-captivea.potx` → le template de **référence** (dernière version). C'est la **seule** source de mise en forme autorisée. Ses **slides d'exemple** (une par masque, plus « Nos bureaux » en FR et en EN) sont les **slides de design** : toute nouvelle slide reprend le design de la slide d'exemple de son masque.
- **Sources** : `02. French PPT to transform/` → PPT dans l'ancienne charte, servent de base de contenu.
- **Sortie** : `04. Render from claude/` → tu y sauvegardes les fichiers transformés.
- (Ignorer `03. English PPT for translation` et `05. Render corrected` pour cette tâche.)

## Étapes

1. **Identifier les fichiers à traiter.**
   Lister les `.pptx` de `02. French PPT to transform` **de façon récursive** (les documents sont souvent rangés dans des **sous-dossiers**). Exclure ceux dont un fichier de **même nom au même emplacement relatif** existe déjà dans `04. Render from claude`. Ne traiter que les restants. **Noter le chemin relatif** (sous-dossiers) de chaque fichier pour le réutiliser à la sauvegarde.

2. **Lire le template.**
   Ouvrir le `.potx` de `01. Template` et inventorier **tous les masques / dispositions (layouts) disponibles**, avec leurs zones (titre, sous-titre, contenu, capsule d'en-tête, pied de page, images, etc.). Les transformations doivent utiliser **uniquement** ces masques — ne créer aucun layout ni style hors template.

3. **Pour chaque fichier source, recréer la présentation dans le nouveau template :**
   - **Réutilisation incrémentale (ne pas tout refaire).** Avant de (re)générer une slide, chercher si une version déjà traitée existe pour cette même slide source :
     1. d'abord dans le **dossier validé `05. Render corrected`** (versions corrigées/validées) ;
     2. sinon dans `04. Render from claude` (rendu précédent).
     Identifier l'équivalence par le **document et la slide** correspondants (même titre / même position / même contenu source). Si une version existe, **la reprendre telle quelle** (copier la slide) au lieu de la reconstruire. Ne (re)générer que les slides **absentes des deux dossiers** ou dont le **contenu source a changé**. Le dossier `05` a toujours priorité sur `04`.
   - **Mapper** chaque slide source vers le masque du template le plus adapté à son type de contenu (couverture, section, contenu simple, deux colonnes, image pleine page, etc.).
   - **Textes : reproduction VERBATIM.** Reprendre le texte des slides sources **mot pour mot**, y compris la **casse**, la **ponctuation**, les **nombres, unités et leur format** (ne pas transformer `114.00 EUR/h HT` en `114,00 €/h HT`, ni `250-350h` en `250 – 350 h`). Aucune reformulation, aucun résumé, aucune « amélioration » de formulation.
   - **Zéro invention de contenu.** Ne **jamais** ajouter de texte absent du source : pas de descriptions, sous-titres, légendes de statistique ou phrases explicatives inventées pour « remplir » une zone. La seule invention autorisée est le **libellé court de la capsule/bandeau d'en-tête** (voir plus bas).
   - **Zéro perte / zéro condensation.** Reproduire **tous** les éléments et sous-points du source. S'ils tiennent mal, réduire la taille ou agrandir la zone — **jamais** supprimer ou fusionner du contenu pour gagner de la place.
   - **Titre ≠ capsule (pas de duplication).** La capsule/bandeau porte le **thème récurrent** (section, court) ; le titre porte **uniquement le sujet spécifique** de la slide. Ne pas répéter le texte de la capsule dans le titre. Si le titre source concatène un fil d'ariane + un sujet, les **scinder** (fil d'ariane → capsule, sujet → titre). Quand la slide porte sur une entité nommée, mettre ce **nom** comme titre.
   - **Slides masquées.** Si une slide est **masquée (hidden)** dans le document source, la recréer puis la **masquer également** dans le document de sortie (conserver son état masqué). ⚠️ **Détection :** l'état masqué se lit sur l'attribut **`show="0"` de la racine `<p:sld …>` de chaque `slideN.xml`** — PAS dans `presentation.xml`. Vérifier chaque slide individuellement (souvent plusieurs slides masquées dans un même document).
   - **Nouvelles zones du masque.** Si un masque comporte une zone absente de la source (typiquement la **capsule / bandeau d'en-tête**), y placer un **libellé court** = le thème/section de la slide (quelques mots, pas une phrase). C'est la **seule** création de texte autorisée ; ne pas s'en servir pour ajouter du contenu de fond.
   - **Respecter le design du template** : polices, couleurs, tailles, espacements, positions définis par les masques. Ne pas réutiliser les styles de l'ancienne charte (hors SmartArt/schémas, voir point 5).
   - **Ajustements autorisés au niveau de la diapo.** Il est interdit de créer de nouveaux masques, mais une fois un masque appliqué, tu as **toute latitude pour adapter les zones existantes du masque** afin d'obtenir le meilleur rendu, tant que polices, couleurs et style restent ceux du template. Sont notamment autorisés :
     - **Redimensionner / repositionner** n'importe quelle zone (texte comme graphique).
     - **Réaffecter une zone** à un autre usage : par ex. écrire un **libellé texte dans une zone prévue pour un chiffre ou un cercle** quand le contenu s'y prête mieux.
     - **Icônes à la place des chiffres.** Tu peux **remplacer les numéros** (dans les cercles/orbites/pastilles ou cartes) par des **icônes pertinentes** quand cela améliore le design. Utiliser les **icônes du pack Lucide** (charte du template : icône recolorisée au rouge/dégradé Captivea).
     - **Supprimer les zones inutiles** du masque (par ex. un sous-titre non nécessaire) et **remonter / réagencer** le contenu restant pour combler l'espace et équilibrer la diapo.
     - Choisir, parmi les masques disponibles, celui qui rend le mieux une fois ces adaptations faites.

4. **Sections + Sommaire : étape SYSTÉMATIQUE à la création (ne pas oublier).**
   - **Identifier d'abord toutes les slides de type SECTION (intercalaires)** du document : slides-titres qui introduisent une partie (souvent une slide sur fond rouge/dégradé, un grand titre seul, un numéro d'étape). Les recréer avec le **masque de type section** du template, **numérotées dans l'ordre** (01, 02, 03…).
   - **Toujours intégrer un sommaire** : s'il n'y en a pas dans le source, en **créer un** avec le **masque de type sommaire**, rempli à partir des **numéros + intitulés des sections identifiées**, dans l'ordre. Le placer **juste après la couverture**. S'il existe déjà, le recréer (pas de doublon).
   - ⚠️ **Ne jamais livrer un document sans sommaire** dès qu'il comporte des sections. C'est une étape obligatoire, à vérifier en fin de production.

5. **SmartArt, schémas, tableaux et diagrammes : ne jamais mettre à plat.**
   Un schéma ou un tableau ne doit **jamais** être transformé en simple texte, en liste à puces ou en cartes.

   **🎯 RÈGLE DE DÉCISION CENTRALE — S'APPUYER SUR LES MASQUES DU TEMPLATE.**
   La méthode par défaut n'est **PAS** de recopier des groupes tels quels sur une toile vide. C'est :
   1. **Analyser la structure** de la slide source : **compter précisément le nombre d'éléments parallèles** (bulles, colonnes, étapes, cartes).
   2. **Choisir le masque dont le NOMBRE de zones correspond EXACTEMENT** à ce nombre : 2 éléments → masque à 2 (Boxed/Circles 2 colonnes) ; **3 éléments → masque à 3** ; 4 → masque à 4. **Ne jamais** faire tenir 3 éléments dans un masque à 2 (ni l'inverse), ni condenser/dédoubler pour rentrer dans un masque au mauvais compte. Si aucun masque n'a le bon nombre, prendre le plus proche au-dessus et laisser une zone vide plutôt que de tasser.
   3. **Dégrouper le contenu source** (ouvrir les groupes, récupérer chaque zone de texte / libellé / valeur / icône individuellement).
   4. **Répartir ce contenu dans les zones/placeholders du masque choisi** — c'est le masque qui porte la mise en page, les couleurs, les polices, les cercles/cartes de la charte. On **remplit** le masque, on ne colle pas un bloc étranger par-dessus.

   - **Recréer via le masque le plus proche = cas par défaut** (la grande majorité des slides). Contenu **verbatim**, aucune invention, rendu **100 % charte**.
   - **Reprendre l'objet d'origine tel quel = exception**, réservée aux **vrais SmartArt** ou **diagrammes complexes** (flux, cycles, schémas relationnels) qu'**aucun masque ne peut représenter** : dans ce cas seulement, réinsérer l'objet puis le **re-styler à la charte** (voir 5a / 5c / 5d).

   **À tenir dans tous les cas :** contenu **fidèle à 100 %**, rendu **entièrement à la nouvelle charte** via les masques (aucun ancien dégradé/couleur/police ne subsiste), slide **remplie harmonieusement**. Le contenu est fidèle, **pas** son ancien design.

   **⛔ Jamais de rouge `#BA131A` en fond + remplacer TOUS les dégradés.** 
   - Ne jamais utiliser la couleur pleine `#BA131A` comme **fond** (slide, forme large, carte, bandeau…). Chaque fois qu'un fond rouge est voulu, utiliser le **dégradé de base de la charte**. `#BA131A` reste autorisé pour texte, traits, icônes, petits accents.
   - **Remplacer TOUS les anciens dégradés ET tous les fonds rouges pleins** (issus de l'ancienne charte ou du contenu transplanté) par le **dégradé de base de la charte**. Aucun ancien dégradé, ni aucun aplat rouge de fond, ne doit subsister — vérifier fonds de slide, formes de fond, bandeaux et grandes zones colorées.

   **⚠️ Attention — la plupart des diagrammes ne sont PAS des SmartArt.** Ce sont très souvent des **diagrammes faits main** : un assemblage de **formes + zones de texte** (rectangles, ronds, flèches, connecteurs), **fréquemment groupés**. Ils sont faciles à rater : si on n'extrait que le texte, on les aplatit sans le vouloir. Il faut donc les **détecter activement**.

   **Comment détecter un diagramme fait main :** la slide contient un **groupe de formes**, ou **plusieurs zones de texte positionnées** pour former une structure, ou des **flèches/connecteurs/formes** disposés spatialement. Dans ce cas → c'est un diagramme (pas du texte libre), et il faut **rapatrier TOUT son contenu** (parcourir aussi l'intérieur des groupes pour n'oublier aucun libellé ni sous-point).

   **Étape préalable obligatoire — classer chaque graphique de la slide source** avant de la reconstruire, et noter le traitement retenu :
   - *SmartArt natif (objet PowerPoint)* → 5a (reprendre le contenu, re-styler à la charte).
   - *Diagramme fait main (formes + zones de texte, souvent groupées)* → 5a (contenu repris + re-stylé charte), sinon 5b (redessiner à la charte **avec 100 % du contenu**). **C'est le cas le plus fréquent.**
   - *Schéma / diagramme* (le sens vient de la disposition ou des liens) → 5b (redessiner).
   - *Tableau / matrice de données* (grille lignes × colonnes) → 5d (reproduire à l'identique).
   - *Icône SVG dans un cercle* → 5c (icône + orbite).
   - *Image / photo* → point 6 (réinsérer sans déformer).
   Aucun graphique ne doit « tomber » par défaut en texte faute d'avoir été détecté et classé.

   **5a. SmartArt natifs OU diagrammes faits main (formes + zones de texte groupées) → reprendre le CONTENU, re-styler à la charte.**
   - Reprendre **tout le contenu et la structure** (toutes les formes, zones de texte, connecteurs, libellés, y compris à l'intérieur des groupes) pour ne **rien perdre**.
   - Méthode : appliquer le masque du template offrant une zone de contenu adaptée, **supprimer les zones de texte de contenu** de ce masque, puis **reprendre l'objet d'origine** (SmartArt ou groupe de formes) dans la zone libérée. Titre, capsule, logo et fond viennent du template.
   - **Re-styler à la NOUVELLE charte (obligatoire).** Remplacer les **anciens dégradés/couleurs** par ceux du template, appliquer les **polices du template**, et **recoloriser les icônes au dégradé de la charte**. Ne **jamais** laisser le diagramme dans son ancien habillage.
   - **Placement propre :** regrouper le contenu et le **mettre à l'échelle dans une zone dédiée, SOUS le titre et la capsule** (par ex. sous ~1,7" de haut), sans **chevaucher** le titre/capsule ni **déborder**, et en **remplissant harmonieusement** la slide (éviter les grands vides). Conserver les proportions. Pour un grand diagramme, préférer le masque *Title only – Wide*.
   - **Photos** intégrées (personnes/équipe) : conservées telles quelles (on ne recolorise pas une photo).
   - **Nuance (slides très simples) :** si la slide ne contient que quelques éléments **parallèles** (ex. 3–4 statistiques ou puces) ou du contenu logé dans des **placeholders du masque source**, préférer une **recréation propre** sur un masque *Circles/Boxed* (le transplant y disperse les éléments ou laisse du vide) — verbatim, sans invention.

   **5b. Schémas / diagrammes → REDESSINER en charte (formes + connecteurs).**
   - **Qu'est-ce qu'un schéma ?** Tout contenu dont le sens vient de la **disposition ou des relations** : flux/flèches, cycle, chronologie/timeline, entonnoir, matrice conceptuelle, pyramide, organigramme, parcours client, processus par étapes.
   - **Test de décision** : si supprimer les flèches / positions / liens fait **perdre le sens** → c'est un schéma → à **redessiner**. Si les éléments sont seulement **parallèles** (aucune relation directionnelle) → des colonnes sont acceptables.
   - **Interdit (= mise à plat) :** convertir un schéma en **liste à puces, en cartes, en simples colonnes *Boxed* ou en tableau**. Même avec un masque du template, cela reste une mise à plat et n'est pas autorisé.
   - **Méthode :** utiliser un masque servant de **toile libre** (« titre seul », « titre seul – wide » pour un grand diagramme, ou « vide »), puis **redessiner le schéma avec des formes et des connecteurs** qui **reproduisent la même structure** (mêmes blocs, même séquence, mêmes liens, mêmes sous-points), aux **couleurs et polices du template**.
   - Conserver **la logique, la structure ET le texte** du schéma source, **sans rien perdre** (tous les blocs, tous les sous-points).
   - **Le redessin doit reproduire 100 % du contenu** du schéma. Si le redessin risque de **condenser ou perdre** des éléments, ne pas redessiner : passer par **5a** (reprendre le contenu d'origine **puis le re-styler à la charte**). Dans les deux cas, contenu **complet** ET habillage **à la nouvelle charte** sont obligatoires.
   - Ne jamais remplacer un diagramme riche (nombreux sous-points, cartes de tarifs, étapes de process) par une version simplifiée en cartes/colonnes : soit 5a (contenu d'origine re-stylé), soit 5b (redessin intégral à la charte).

   **5c. Icônes SVG dans un cercle → icône reprise + recolorisée + orbite du template.**
   - Quand une slide source contient une **icône SVG placée dans un cercle**, réutiliser l'**icône d'origine** (son dessin) et la centrer dans un **cercle « orbite »** du template (le cercle décoratif des masques de type *Circles*).
   - **Recoloriser l'icône au dégradé / aux couleurs de la charte** (ne pas la laisser dans sa couleur d'origine).
   - **Masquer le numéro** de l'orbite : régler la **couleur du texte du numéro identique à sa couleur de fond** pour qu'il soit invisible. Résultat : l'orbite du template entoure l'icône (recolorée), sans numéro visible.
   - Conserver les proportions de l'icône ; ne pas la déformer.

   **5d. Tableaux / matrices de données → reproduire à l'IDENTIQUE.**
   - Reproduire le tableau **strictement à l'identique** : **mêmes lignes et colonnes**, **même en-têtes**, et **texte de chaque cellule repris mot pour mot** (aucune reformulation, aucun résumé, aucune condensation).
   - **Ne pas déplacer** un texte d'une cellule à une autre : chaque contenu reste dans sa cellule d'origine (même position ligne/colonne).
   - **Conserver les proportions** du tableau (structure et dimensions relatives) ; ne pas redimensionner arbitrairement les colonnes/lignes.
   - Seul le **style** est adapté à la charte (couleurs d'en-tête, police du template, filets) — jamais le contenu ni la structure.

6. **Images de contenu : réinsérer sans déformer.**
   - **Ne PAS réimporter les illustrations « amico » / Storyset / Freepik** (petits personnages, illustrations vectorielles génériques). Les détecter (SVG contenant `freepik` / `storyset` / `amico`, ou grandes illustrations de personnages) et les **supprimer** : elles ne font pas partie de la charte. Les petites **icônes** fonctionnelles restent conservées (recolorisées à la charte).
   - Réinsérer les images de contenu des slides sources dans la zone de contenu du masque, en **remplaçant la zone de texte** par l'image.
   - **Conserver strictement les proportions** de l'image (pas d'étirement) ; recadrer/ajuster si besoin pour un rendu propre.
   - Pour une **grande image ou un grand diagramme**, utiliser le masque **« Standard - Title only - Wide »** (titre déporté, capsule conservée) afin de **libérer un maximum d'espace**.
   - **Retirer** uniquement les anciens logos et éléments de branding de l'ancienne charte ; ils sont remplacés par ceux portés par les masques du template.

7. **Nommage : identique + convention de langue.**
   Le fichier de sortie porte **exactement le même nom** que le fichier source.
   La charte de nommage est : **`XX - Nom du document`**, où `XX` est la langue (`FR` ou `EN`) et le **nom du document est identique en français et en anglais** (seul le préfixe de langue change).
   Exemple générique : `FR - Nom du document.pptx` (source FR) → sortie `FR - Nom du document.pptx` ; sa version anglaise correspondante serait `EN - Nom du document.pptx`.

8. **Notes et commentaires : à reprendre systématiquement.**
   Pour chaque slide, **reporter à l'identique les notes du présentateur (speaker notes) et les commentaires** présents sur la slide source correspondante. Aucune note ni aucun commentaire ne doit être perdu lors de la transformation.

9. **Slides identiques entre documents (bibliothèque `unique_slides` + Excel de suivi).**
   Objectif : repérer les slides **réutilisées à l'identique dans plusieurs documents**, les mutualiser et les tracer.
   - **Fichiers de suivi** (dans `04. Render from claude/`) :
     - le dossier **`unique_slides/`** : une **copie de chaque slide unique**, dans un `.pptx` portant le nom de la slide. Cette copie doit provenir de la **version VALIDÉE** de la slide (dossier `05. Render corrected`), jamais de mon propre rendu `04`.
     - le fichier **`Slides uniques - suivi.xlsx`**.
   - **Structure de l'Excel (format extensible à N documents)** : une **ligne par utilisation** d'une slide unique dans un document. Colonnes : *Nom de la slide* · *Fichier unique (unique_slides)* · **Rôle** (`Source` = document validé d'origine, `Réutilisation` = document supplémentaire) · *Document* · *Position dans le document* · *Date*. Ainsi une même slide apparaît sur **plusieurs lignes** : une ligne `Source` (le document validé d'origine) et une ligne `Réutilisation` par document supplémentaire — et on peut en ajouter autant que nécessaire.
   - **Le document d'origine (validé) est la SOURCE.** Le chemin de référence est la version validée dans `05. Render corrected`. Quand une slide identique est détectée dans un nouveau document, écrire **deux (ou plus) lignes** : la ligne `Source` (document validé + sa position) si elle n'existe pas déjà, **et** la ligne `Réutilisation` (nouveau document + sa position).
   - **D'où viennent les positions :**
     - Ligne `Source` → position lue dans le **document validé de `05. Render corrected`** (référence qui fait foi).
     - Lignes `Réutilisation` → position lue dans le **document traité tel que produit dans `04. Render from claude`** (le rendu en cours), **pas** dans `05`. Ces positions peuvent être recalculées une fois le document finalisé dans le render.
   - **Réutilisation réelle** : pour une slide identique, **copier la slide VALIDÉE depuis `05. Render corrected`** (pas la recréer, pas prendre celle de `04`) et l'insérer telle quelle dans le nouveau document.
   - Si la slide unique n'existe pas encore dans `unique_slides/`, l'y **extraire depuis la version validée `05`** sous un `.pptx` à son nom.
   - Détecter l'identité par le **contenu** (même titre + mêmes éléments), pas seulement par le nom.

10. **Sauvegarde (en respectant l'arborescence).**
   Enregistrer chaque `.pptx` transformé dans `04. Render from claude/`, en **recréant la même arborescence de sous-dossiers** que dans `02. French PPT to transform`. Si un fichier source est dans `02. French PPT to transform/<sous-dossier>/…`, la sortie va dans `04. Render from claude/<sous-dossier>/…`. **Créer les dossiers manquants** si l'arborescence n'existe pas encore dans render.

11. **Vérification (obligatoire).**

   **🔁 Passe post-création OBLIGATOIRE — re-parcourir chaque slide produite après coup et corriger :**
   - **Dégradés & fonds** : vérifier qu'**aucun ancien dégradé** ni **aucun fond rouge plein** ne subsiste ; tous doivent être passés au **dégradé de base de la charte** (jamais de `#BA131A` en aplat de fond). Corriger les fonds de slide, formes de fond, bandeaux et grandes zones colorées.
   - **Bon masque appliqué** : vérifier que **chaque slide utilise le masque correct**, avec le **bon nombre de zones** (autant que d'éléments parallèles : 3 éléments → masque à 3). Corriger tout contenu tassé dans un masque au mauvais compte.
   - **Slides récurrentes réutilisées** : vérifier que chaque slide déjà validée / déjà utilisée dans un autre document (interlocuteurs, équipe, chronologie, références, bureaux, sections…) a bien été **reprise du `05`/`unique_slides`** et non recréée.
   - **Polices : aucune police résiduelle de l'ancienne charte.** Rechercher et remplacer toute police résiduelle (par ex. **Trebuchet MS**, ou toute police hors template) par les **polices du template**. Vérifier le contenu transplanté, qui conserve souvent ses anciennes polices.
   - Effectuer ces corrections **avant** de considérer le fichier comme terminé.

   Pour chaque fichier produit :
   - Confirmer que tous les masques utilisés proviennent bien du template.
   - (À partir du 2e document) Confirmer que les **slides identiques** ont été **tracées dans l'Excel** et **copiées dans `unique_slides/`**, et réutilisées plutôt que recréées.
   - Confirmer qu'aucun texte source n'a été perdu ou déformé.
   - Confirmer qu'un **sommaire** est présent (celui du source, ou un sommaire généré depuis les slides de section s'il n'y en avait pas).
   - Confirmer que **chaque diagramme a été détecté** (y compris les diagrammes faits main en formes + zones de texte groupées) et qu'**aucun n'a été aplati** en texte : contenu repris (5a) ou redessiné (5b) avec 100 % du contenu ; tableaux reproduits à l'identique (5d).
   - Confirmer, pour chaque diagramme, que **tout le contenu du source est présent** (aucun libellé ni sous-point perdu, y compris ceux nichés dans des groupes).
   - **Confirmer que TOUT est passé à la nouvelle charte** : aucun ancien dégradé/couleur ne subsiste, icônes recolorisées au dégradé de la charte, polices du template. Aucun visuel ne doit conserver l'ancien habillage.
   - Confirmer que **le rendu remplit harmonieusement chaque slide** (pas d'éléments éparpillés, pas de grands vides, pas de contenu minuscule).
   - **Gate QA visuel (obligatoire)** : pour chaque schéma et chaque tableau, comparer **capture source ↔ rendu côte à côte** et valider que blocs, liens, flèches, séquence, lignes/colonnes et texte de cellule sont bien reproduits — pas seulement que le texte est présent.
   - Confirmer que **les images de contenu ont été réinsérées sans déformation** (proportions conservées).
   - Confirmer que **les notes du présentateur et les commentaires** ont bien été repris sur chaque slide.
   - Confirmer que les **slides masquées du source restent masquées** dans le rendu.
   - Confirmer qu'aucun ancien logo/branding ne subsiste.
   - Générer un aperçu (rendu image des slides) et le contrôler visuellement.
   - Fournir un court récapitulatif : fichiers traités, fichiers ignorés (déjà présents), points à revoir manuellement.

## Contraintes clés
- **Masque = bon nombre de zones** : compter les éléments parallèles de la slide et choisir le masque au **nombre exact** (3 éléments → masque à 3, jamais 2). Ne pas tasser ni dédoubler pour rentrer dans un mauvais compte.
- **Réutilisation systématique des slides récurrentes** : avant de (re)créer, vérifier pour CHAQUE slide si une version validée/déjà utilisée existe (dossier `05` puis `unique_slides`, ex. interlocuteurs, équipe, chronologie, références, bureaux, sections…) et la **réutiliser telle quelle**. Contrôler après coup que ces slides ont bien été reprises et non recréées.
- **Priorité aux masques du template** : pour chaque slide, choisir le masque existant le plus proche, **dégrouper** le contenu source et le **répartir dans les placeholders/zones du masque**. Ne **jamais** se contenter de recopier un groupe entier sur une toile vide. Reprendre un objet tel quel est une **exception** (vrais SmartArt / diagrammes complexes non représentables par un masque), puis re-stylé à la charte.
- Utiliser **uniquement** les masques du template (`01. Template`) — aucun nouveau masque. En revanche, **au sein d'un masque appliqué, adaptation libre des zones existantes** (redimensionner, repositionner, réaffecter une zone à du texte, supprimer les zones inutiles, remonter/réagencer le contenu) pour améliorer le rendu, sans changer polices/couleurs/style du template.
- Textes **verbatim** (casse, ponctuation, nombres, unités et format inchangés) ; **aucune invention** de contenu sauf le libellé court de la capsule ; **aucune condensation** ni perte d'éléments.
- **Titre ≠ capsule** : la capsule porte le thème/section, le titre le sujet spécifique — jamais de duplication.
- **Contenu fidèle, design à la nouvelle charte** : reprendre 100 % du contenu, mais **re-habiller entièrement au template** — remplacer les anciens dégradés/couleurs, appliquer les polices du template, **recoloriser les icônes au dégradé de la charte**. Le contenu est fidèle, **pas** son ancien design. Aucun visuel ne doit rester dans l'ancienne charte.
- **Résultat propre prioritaire** : chaque slide doit **remplir harmonieusement** l'espace à la charte — jamais d'éléments éparpillés, de grands vides ou de contenu minuscule. La méthode (transplant / redessin / recréation) n'est qu'un moyen au service de ce résultat.
- **Sommaire obligatoire** : si le source n'en a pas, en générer un via le masque de type sommaire, à partir des numéros et intitulés des slides de section.
- **Détecter les diagrammes faits main** (formes + zones de texte groupées) — cas le plus fréquent, à ne pas confondre avec du texte libre — et en reprendre **100 % du contenu**, puis le re-styler à la charte (ou le redessiner à la charte).
- **Rien n'est mis à plat** : diagrammes repris (contenu) puis re-stylés charte, ou redessinés en formes+connecteurs (jamais en liste/cartes/colonnes) ; tableaux/matrices reproduits à l'identique côté contenu (mêmes cellules, texte mot pour mot), stylés à la charte. Un schéma ≠ des colonnes ; une matrice de données = un tableau, pas des formes.
- **Images de contenu réinsérées sans déformation** (proportions conservées) ; **supprimer** uniquement les logos/branding de l'ancienne charte.
- **Réutiliser avant de recréer** : si une slide existe déjà (priorité au dossier validé `05. Render corrected`, sinon `04. Render from claude`), la récupérer telle quelle ; ne créer que ce qui manque ou a changé.
- **Respecter l'arborescence** : parcourir `02. French PPT to transform` de façon récursive et **recréer la même structure de sous-dossiers** dans `04. Render from claude` (créer les dossiers manquants) pour y ranger chaque sortie.
- Ne **jamais écraser** un fichier déjà présent dans `04. Render from claude`.
