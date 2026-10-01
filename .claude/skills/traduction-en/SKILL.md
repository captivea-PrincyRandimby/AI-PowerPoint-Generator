---
name: traduction-en
description: Produire la version anglaise (US) d'un document FR validé de 05. Render corrected, en traduisant uniquement le texte (design intact), avec le wording des anciens EN de 03, la mémoire de traduction et les slides de design EN du template. Utiliser quand l'utilisateur demande une traduction EN / version anglaise.
argument-hint: "[chemin du document FR validé dans 05]"
---

# Traduction EN — texte seul, design intact

Règles de fond : **lire `00. Prompts/02 - Traduction EN des documents FR validés.md`**.
Document : `$ARGUMENTS` (si vide : `python tools/todo.py`, section Tâche 2).

⚠ Toujours partir du FR **validé** (`05. Render corrected`), jamais de `04`.
⚠ Un document déjà en anglais (ex. `EN - Sales - MMB Market`) ne se traduit pas.

1. `python tools/translate.py export "<FR validé>"` → `work/<doc>/translate.json` + `work/<doc>/ref_en.md`
   (référence EN trouvée automatiquement dans `03`, sinon `--ref "<fichier>"`).
   Le champ `"en"` est **pré-rempli** quand c'est possible (`"source"` indique l'origine, **à relire**) :
   `glossaire` (terminologie imposée) · `template` (slides de design du template existant en FR et EN) ·
   `memoire` (`tools/memoire_traduction.json`, traductions déjà validées). `"suggestions"` = traductions
   validées ailleurs pour un texte dont le sens dépend du contexte (choisir, ne pas appliquer à l'aveugle).
2. `python tools/tracking.py find "<FR validé>" --en` : slides déjà traduites dans `unique_slides_EN/` → reprendre leur wording.
3. Remplir chaque champ `"en"` encore vide de `translate.json` :
   - wording **exact** de `ref_en.md` quand il existe ; sinon anglais US professionnel → lister ces entrées dans le récap ;
   - ⚠ l'ancien EN n'a pas toujours le même contenu à la même position (autre pays, autres tarifs, colonnes
     réordonnées) : ne reprendre une formulation que si elle traduit bien le FR, chiffres identiques ;
   - chiffres, prix, unités, dates, noms propres **inchangés** ; `\n` = retour à la ligne à conserver ;
   - entrées avec `"runs"` (formatage mixte) : remplir `"en_runs"` avec le même nombre de morceaux ;
   - notes du présentateur (`…/notes/…`) traduites aussi.
   Pour un gros document : traiter par lots de slides, en éditant le JSON (ne jamais changer les `id`).
4. **STOP → montrer à l'utilisateur les traductions libres (sans référence) et attendre sa validation.**
5. `python tools/translate.py apply "<FR validé>"` → `04/<miroir>/EN - <nom>.pptx`.
   Les slides issues d'une slide de design FR du template qui a une jumelle EN (ex. « Nos bureaux ») sont
   remplacées automatiquement par la version EN officielle du template (mise en page prévue pour l'anglais).
6. `python tools/audit.py "<EN>" --en "<FR validé>"` (0 erreur) puis `python tools/render.py png "<EN>"` et
   **regarder** la planche : débordements (l'anglais est souvent plus court, parfois plus long), texte FR résiduel.
7. Slides EN réutilisables : `tracking.py add … --en` ; enrichir `tools/memoire_traduction.json` avec les nouvelles
   paires validées ; récapitulatif (traductions libres, réutilisations, points à vérifier).
