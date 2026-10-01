# Prompt 02 — Traduction EN des documents FR validés

## Objectif
Produire la **version anglaise** de chaque document **FR validé** (`05. Render corrected`), en **traduisant uniquement les textes** et en s'appuyant sur les **anciens fichiers EN** (`03. English PPT for translation`) pour reprendre le **wording exact**. Le **design (nouvelle charte)** des slides FR validées est **conservé à l'identique** — seule la langue change.

## Dossiers de référence
- **Source à traduire** : `05. Render corrected/` → documents **FR validés** (design déjà à la nouvelle charte). C'est la base de la traduction.
- **Référence de wording** : `03. English PPT for translation/` → anciens PPT **en anglais**, utilisés pour reprendre les **formulations officielles EN** (terminologie exacte). Servent uniquement de source de texte, **pas** de design.
- **Sortie** : `04. Render from claude/` → fichiers **EN**, en recréant la **même arborescence de sous-dossiers** que le source (créer les dossiers manquants).
- **Bibliothèque de slides EN réutilisables** : `04. Render from claude/unique_slides_EN/` + fichier de suivi `Slides uniques EN - suivi.xlsx`.

## Principe directeur
- **Traduire le TEXTE uniquement.** Ne jamais modifier le design, la mise en page, le masque, les couleurs, les dégradés, les images, les diagrammes ni les positions des slides FR validées. On part de la slide validée et on **remplace le texte FR par son équivalent EN**.
- **Wording exact prioritaire.** Quand une formulation existe dans le fichier EN de référence, la **reprendre mot pour mot** (terminologie, tournures, casse). Ne re-traduire librement que ce qui n'a **pas** d'équivalent dans la référence — dans un anglais professionnel et cohérent avec le reste.
- **Données inchangées.** Nombres, chiffres, prix, unités, dates, noms propres : identiques au FR (sauf format anglophone si la référence EN le fait, ex. séparateurs).

## Étapes

1. **Identifier les documents à traduire.**
   Lister récursivement les `.pptx` de `05. Render corrected` (sous-dossiers inclus). Exclure ceux dont la version **EN** existe déjà au même emplacement relatif dans la sortie. Noter le chemin relatif pour la sauvegarde.

2. **Associer le fichier EN de référence.**
   Pour chaque document FR validé, retrouver le **fichier EN correspondant** dans `03. English PPT for translation` (même offre / même nom de document). Il servira de source de wording.

3. **Traduire slide par slide (design conservé).**
   Pour chaque slide du document FR validé :
   - **Conserver intégralement le visuel** : masque, mise en page, formes, couleurs/dégradés (charte), images, diagrammes, tableaux, positions. Aucune retouche graphique.
   - **Retrouver la slide/le bloc correspondant** dans le fichier EN de référence (par **contenu** et/ou position ; l'ordre peut différer).
   - **Reprendre le wording officiel EN** de la référence, bloc de texte par bloc de texte (titres, capsules, puces, libellés de diagramme, cellules de tableau).
   - **Sans correspondance** (contenu nouveau/absent de l'ancien EN) : traduire fidèlement en **anglais professionnel**, et le **signaler** dans le récapitulatif.
   - **Notes du présentateur & commentaires** : les traduire également (wording EN de référence s'il existe).

4. **Slides masquées.** Conserver l'état **masqué** (`show="0"`) des slides masquées dans le source FR.

5. **Réutilisation des slides déjà traduites (même logique que la création).**
   - Avant de traduire une slide, vérifier si sa **version EN** existe déjà :
     1. dans `unique_slides_EN/` (bibliothèque des slides EN validées/réutilisables) ;
     2. sinon dans un document EN déjà produit (`04. Render from claude`).
     Si oui → **réutiliser la slide EN telle quelle** au lieu de la re-traduire.
   - **Mettre de côté les slides EN réutilisables** : quand une slide traduite est susceptible de revenir dans d'autres documents (ex. success story, interlocuteurs, références, sections, bureaux…), en **copier une version dans `unique_slides_EN/`** sous un `.pptx` à son nom.
   - **Tracer dans `Slides uniques EN - suivi.xlsx`** (même format extensible que le suivi FR) : une **ligne par utilisation**, colonnes *Nom de la slide* · *Fichier unique (unique_slides_EN)* · **Rôle** (`Source` = 1er document validé d'origine, `Réutilisation` = document supplémentaire) · *Document* · *Position* · *Date*. Prévoir N documents (1 ligne Source + 1 ligne Réutilisation par document).

6. **Nommage : préfixe de langue EN.**
   Le fichier de sortie porte le **même nom que le source, avec le préfixe `EN`** (charte de nommage `XX - Nom du document`, nom identique en FR et EN, seul le préfixe change). Exemple : `FR - Nom du document.pptx` → `EN - Nom du document.pptx`.

7. **Sauvegarde (arborescence miroir).**
   Enregistrer chaque `.pptx` EN dans la sortie en **recréant la même arborescence de sous-dossiers** que le source ; créer les dossiers manquants.

8. **🔁 Passe de vérification post-traduction (OBLIGATOIRE).**
   Re-parcourir chaque slide produite et corriger :
   - **Aucun texte FR résiduel** : tout le texte visible ET les notes/commentaires sont en anglais.
   - **Wording conforme à la référence EN** là où elle existe (pas de re-traduction divergente).
   - **Design inchangé** : aucune modification visuelle non voulue par rapport à la slide FR validée (masque, charte, dégradés, images, diagrammes, positions).
   - **Données identiques** au FR (chiffres, prix, unités, dates).
   - **Slides masquées** toujours masquées.
   - **Polices du template** (aucune police résiduelle hors charte, ex. Trebuchet MS).
   - Générer un **aperçu** (rendu image) et le contrôler visuellement.
   - Fournir un court récapitulatif : documents traités, slides sans correspondance EN (traduites librement, à revoir), slides réutilisées, points à vérifier.

## Contraintes clés
- **Texte uniquement traduit** ; le **design validé (nouvelle charte) reste intact**.
- **Wording EXACT** repris de `03. English PPT for translation` en priorité ; traduction libre seulement à défaut, et signalée.
- **Données/chiffres inchangés**.
- **Réutiliser avant de re-traduire** (bibliothèque `unique_slides_EN`, priorité aux slides EN déjà validées).
- **Slides masquées** conservées ; **notes/commentaires** traduits.
- **Nommage `EN - …`** et **arborescence miroir** ; ne jamais écraser une version EN déjà présente.
