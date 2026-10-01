# Template de référence — `2026-template-captivea.potx`

28 masques · 29 slides de design · format 13.33 x 7.5 in.

Zones communes : `idx 0` = titre, `idx 13` = capsule (bandeau d'en-tête), numéro de slide.
Images : `catalog/layouts/` (zones annotées) et `catalog/designs/` (slides de design).

## Slides de design (toute nouvelle slide part de la slide de design de son masque)

| n° | masque | langue | éléments de design en plus du masque | aperçu |
|---|---|---|---|---|
| 1 | 1_Main Title |  | 0 | Main Title |
| 2 | Section Title |  | 1 | Section Title |
| 3 | Summary |  | 0 | Summary |
| 4 | Standard - 1 column |  | 0 | Standard - 1 column |
| 5 | Standard - 2 columns |  | 0 | Standard - 2 columns |
| 6 | Standard - 2 columns with subititle |  | 0 | Standard - 2 columns with subititle |
| 7 | Standard - Title only |  | 0 | Standard - Title only |
| 8 | Standard - Title only - Wide |  | 0 |  |
| 9 | Standard - Empty |  | 1 | Standard - Empty |
| 10 | Standard - 1/3 2/3 columns |  | 0 | Standard - 1/3 2/3 columns |
| 11 | 1_Standard -  2/3 1/3 columns |  | 0 | Standard - 1/3 2/3 columns |
| 12 | Boxed - 2 columns |  | 0 | Boxed - 2 columns |
| 13 | Boxed - 2 columns with subtitle |  | 0 | Boxed - 2 columns with subtitle |
| 14 | Boxed - 3 columns |  | 0 | Boxed - 3 columns |
| 15 | Boxed - 3 columns with subtitle |  | 0 | Boxed - 3 columns with subtitle |
| 16 | Boxed - 4 columns |  | 0 | Boxed - 4 columns |
| 17 | Boxed - 4 columns with subtitle |  | 0 | Boxed - 4 columns with subtitle |
| 18 | Boxed - 3 columns X2 |  | 0 | Boxed - 3 columns X2 |
| 19 | 1_Boxed - 2 columns X4 |  | 0 | 1_Boxed - 2 columns X4 |
| 20 | Circles - 2 columns |  | 0 | Circles - 2 columns |
| 21 | Circles - 3 columns |  | 0 | Circles - 3 columns |
| 22 | Circles - 4 columns |  | 0 | Circles - 4 columns |
| 23 | Circles - 2 columns X2 |  | 0 | Circles - 2 columns X2 |
| 24 | Circles - 2 columns X2 |  | 0 |  |
| 25 | Design - Circle left |  | 0 | 1_Circles - 2 columns X2 |
| 26 | Design - Arrow down |  | 0 | 2_Circles - 2 columns X2 |
| 27 | 3_Circles - 2 columns X2 |  | 0 | 3_Circles - 2 columns X2 |
| 28 | Disposition personnalisée | fr | 23 | Amérique du Nord / Africa / Europe / Asie |
| 29 | Disposition personnalisée | en | 23 | North America / Africa / Europe / Asia |

Réutiliser une slide de design AVEC son contenu : `"mode": "design"` + `"design": "bureaux_fr"` / `"bureaux_en"` / n° ci-dessus.

## Masques

### [0] 1_Main Title

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 0 | titre | 0.76, 4.11 | 11.81 x 1.61 |
| 1 | contenu | 0.76, 5.79 | 11.81 x 1.32 |

### [1] Section Title

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 2.13 | 11.81 x 1.97 |
| 1 | contenu | 0.76, 4.36 | 11.81 x 1.64 |
| 14 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [2] Summary
*Éléments parallèles : **10***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15]
2. idx [16, 17]
3. idx [18, 19]
4. idx [20, 21]
5. idx [22, 23]
6. idx [26, 27]
7. idx [24, 25]
8. idx [28, 29]
9. idx [30, 31]
10. idx [32, 33]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | pastille/cercle (numero ou icone) | 0.76, 2.84 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 1.54, 2.84 | 4.73 x 0.68 |
| 16 | pastille/cercle (numero ou icone) | 7.07, 2.84 | 0.69 x 0.68 |
| 17 | sous-titre de colonne | 7.85, 2.84 | 4.73 x 0.68 |
| 18 | pastille/cercle (numero ou icone) | 0.76, 3.63 | 0.69 x 0.68 |
| 19 | sous-titre de colonne | 1.54, 3.63 | 4.73 x 0.68 |
| 20 | pastille/cercle (numero ou icone) | 7.07, 3.63 | 0.69 x 0.68 |
| 21 | sous-titre de colonne | 7.85, 3.63 | 4.73 x 0.68 |
| 22 | pastille/cercle (numero ou icone) | 0.76, 4.42 | 0.69 x 0.68 |
| 23 | sous-titre de colonne | 1.54, 4.42 | 4.73 x 0.68 |
| 24 | pastille/cercle (numero ou icone) | 7.07, 4.42 | 0.69 x 0.68 |
| 25 | sous-titre de colonne | 7.85, 4.42 | 4.73 x 0.68 |
| 26 | pastille/cercle (numero ou icone) | 0.76, 5.2 | 0.69 x 0.68 |
| 27 | sous-titre de colonne | 1.53, 5.2 | 4.73 x 0.68 |
| 28 | pastille/cercle (numero ou icone) | 7.07, 5.2 | 0.69 x 0.68 |
| 29 | sous-titre de colonne | 7.84, 5.2 | 4.73 x 0.68 |
| 30 | pastille/cercle (numero ou icone) | 0.76, 5.99 | 0.69 x 0.68 |
| 31 | sous-titre de colonne | 1.53, 5.99 | 4.73 x 0.68 |
| 32 | pastille/cercle (numero ou icone) | 7.07, 5.99 | 0.69 x 0.68 |
| 33 | sous-titre de colonne | 7.84, 5.99 | 4.73 x 0.68 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [3] Standard - 1 column

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 1 | contenu | 0.76, 2.6 | 11.81 x 4.15 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [4] Standard - 2 columns

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 1 | contenu | 0.76, 2.59 | 5.67 x 4.17 |
| 2 | contenu | 6.91, 2.59 | 5.67 x 4.17 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [5] Standard - 2 columns with subititle

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 1 | sous-titre de colonne | 0.76, 2.57 | 5.64 x 0.82 |
| 3 | sous-titre de colonne | 6.9, 2.57 | 5.67 x 0.82 |
| 2 | contenu | 0.76, 3.47 | 5.64 x 3.31 |
| 4 | contenu | 6.9, 3.47 | 5.67 x 3.31 |
| 14 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [6] Standard - 3 columns

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 15 | sous-titre de colonne | 0.76, 2.68 | 3.54 x 0.68 |
| 19 | sous-titre de colonne | 4.9, 2.68 | 3.54 x 0.68 |
| 17 | sous-titre de colonne | 9.03, 2.68 | 3.54 x 0.68 |
| 16 | contenu | 0.76, 3.5 | 3.54 x 3.18 |
| 20 | contenu | 4.9, 3.5 | 3.54 x 3.18 |
| 18 | contenu | 9.03, 3.5 | 3.54 x 3.18 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [7] Standard - Title only

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [8] Standard - Title only - Wide

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 0 | titre | 4.95, 0.59 | 7.62 x 0.93 |
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 14 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [9] Standard - Empty

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [10] Standard - 1/3 2/3 columns

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.47 | 4.3 x 1.19 |
| 1 | contenu | 5.82, 1.47 | 6.75 x 5.23 |
| 2 | contenu | 0.76, 2.83 | 4.3 x 3.85 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [11] 1_Standard -  2/3 1/3 columns

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 1 | contenu | 0.76, 2.59 | 6.75 x 4.11 |
| 14 | contenu | 7.83, 2.59 | 4.75 x 4.11 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [12] Boxed - 2 columns
*Éléments parallèles : **2***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [17, 18, 19]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 2.81 | 0.69 x 0.68 |
| 17 | pastille/cercle (numero ou icone) | 7.06, 2.81 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 3.68 | 5.31 x 0.68 |
| 18 | sous-titre de colonne | 7.06, 3.68 | 5.31 x 0.68 |
| 16 | contenu | 0.96, 4.5 | 5.31 x 1.81 |
| 19 | contenu | 7.06, 4.5 | 5.31 x 1.81 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [13] Boxed - 2 columns with subtitle
*Éléments parallèles : **2***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [24, 25, 26]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | sous-titre | 0.76, 2.51 | 11.81 x 0.91 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 3.67 | 0.69 x 0.68 |
| 24 | pastille/cercle (numero ou icone) | 7.06, 3.67 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 4.43 | 5.34 x 0.68 |
| 25 | sous-titre de colonne | 7.06, 4.43 | 5.34 x 0.68 |
| 16 | contenu | 0.96, 5.15 | 5.34 x 1.49 |
| 26 | contenu | 7.06, 5.15 | 5.34 x 1.49 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [14] Boxed - 3 columns
*Éléments parallèles : **3***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [20, 21, 22]
3. idx [17, 18, 19]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 2.81 | 0.69 x 0.68 |
| 20 | pastille/cercle (numero ou icone) | 4.99, 2.81 | 0.69 x 0.68 |
| 17 | pastille/cercle (numero ou icone) | 9.03, 2.81 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 3.68 | 3.35 x 0.68 |
| 21 | sous-titre de colonne | 4.99, 3.68 | 3.35 x 0.68 |
| 18 | sous-titre de colonne | 9.03, 3.68 | 3.35 x 0.68 |
| 16 | contenu | 0.96, 4.5 | 3.35 x 1.81 |
| 22 | contenu | 4.99, 4.5 | 3.35 x 1.81 |
| 19 | contenu | 9.03, 4.5 | 3.35 x 1.81 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [15] Boxed - 3 columns with subtitle
*Éléments parallèles : **3***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [20, 21, 22]
3. idx [17, 18, 19]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | sous-titre | 0.76, 2.51 | 11.81 x 0.91 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 3.67 | 0.69 x 0.68 |
| 20 | pastille/cercle (numero ou icone) | 4.99, 3.67 | 0.69 x 0.68 |
| 17 | pastille/cercle (numero ou icone) | 9.03, 3.67 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 4.43 | 3.35 x 0.68 |
| 21 | sous-titre de colonne | 4.99, 4.43 | 3.35 x 0.68 |
| 18 | sous-titre de colonne | 9.03, 4.43 | 3.35 x 0.68 |
| 16 | contenu | 0.96, 5.15 | 3.35 x 1.49 |
| 22 | contenu | 4.99, 5.15 | 3.35 x 1.49 |
| 19 | contenu | 9.03, 5.15 | 3.35 x 1.49 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [16] Boxed - 4 columns
*Éléments parallèles : **4***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [20, 21, 22]
3. idx [23, 24, 25]
4. idx [17, 18, 19]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 2.81 | 0.69 x 0.68 |
| 20 | pastille/cercle (numero ou icone) | 4.0, 2.81 | 0.69 x 0.68 |
| 23 | pastille/cercle (numero ou icone) | 6.98, 2.81 | 0.69 x 0.68 |
| 17 | pastille/cercle (numero ou icone) | 10.01, 2.81 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 3.68 | 2.38 x 0.68 |
| 21 | sous-titre de colonne | 4.0, 3.68 | 2.38 x 0.68 |
| 24 | sous-titre de colonne | 6.98, 3.68 | 2.38 x 0.68 |
| 18 | sous-titre de colonne | 10.01, 3.68 | 2.38 x 0.68 |
| 16 | contenu | 0.96, 4.5 | 2.38 x 1.81 |
| 22 | contenu | 4.0, 4.5 | 2.38 x 1.81 |
| 25 | contenu | 6.98, 4.5 | 2.38 x 1.81 |
| 19 | contenu | 10.01, 4.5 | 2.38 x 1.81 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [17] Boxed - 4 columns with subtitle
*Éléments parallèles : **4***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [27, 28, 29]
3. idx [30, 31, 32]
4. idx [24, 25, 26]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | sous-titre | 0.76, 2.51 | 11.81 x 0.91 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 3.67 | 0.69 x 0.68 |
| 27 | pastille/cercle (numero ou icone) | 4.01, 3.67 | 0.69 x 0.68 |
| 30 | pastille/cercle (numero ou icone) | 7.01, 3.67 | 0.69 x 0.68 |
| 24 | pastille/cercle (numero ou icone) | 10.01, 3.67 | 0.69 x 0.68 |
| 15 | sous-titre de colonne | 0.96, 4.43 | 2.39 x 0.68 |
| 28 | sous-titre de colonne | 4.01, 4.43 | 2.39 x 0.68 |
| 31 | sous-titre de colonne | 7.01, 4.43 | 2.39 x 0.68 |
| 25 | sous-titre de colonne | 10.01, 4.43 | 2.39 x 0.68 |
| 16 | contenu | 0.96, 5.15 | 2.39 x 1.49 |
| 29 | contenu | 4.01, 5.15 | 2.39 x 1.49 |
| 32 | contenu | 7.01, 5.15 | 2.39 x 1.49 |
| 26 | contenu | 10.01, 5.15 | 2.39 x 1.49 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [18] Boxed - 3 columns X2
*Éléments parallèles : **6***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [14, 15, 16]
2. idx [20, 21, 22]
3. idx [17, 18, 19]
4. idx [23, 24, 25]
5. idx [29, 30, 31]
6. idx [26, 27, 28]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 14 | pastille/cercle (numero ou icone) | 0.96, 2.84 | 0.53 x 0.52 |
| 15 | sous-titre de colonne | 1.49, 2.78 | 2.82 x 0.68 |
| 20 | pastille/cercle (numero ou icone) | 4.99, 2.84 | 0.53 x 0.52 |
| 21 | sous-titre de colonne | 5.52, 2.78 | 2.82 x 0.68 |
| 17 | pastille/cercle (numero ou icone) | 9.03, 2.84 | 0.53 x 0.52 |
| 18 | sous-titre de colonne | 9.56, 2.78 | 2.82 x 0.68 |
| 16 | contenu | 0.96, 3.48 | 3.35 x 1.08 |
| 22 | contenu | 4.99, 3.48 | 3.35 x 1.08 |
| 19 | contenu | 9.03, 3.48 | 3.35 x 1.08 |
| 24 | sous-titre de colonne | 1.49, 4.94 | 2.82 x 0.68 |
| 30 | sous-titre de colonne | 5.52, 4.94 | 2.82 x 0.68 |
| 27 | sous-titre de colonne | 9.56, 4.94 | 2.82 x 0.68 |
| 23 | pastille/cercle (numero ou icone) | 0.96, 5.0 | 0.53 x 0.52 |
| 29 | pastille/cercle (numero ou icone) | 4.99, 5.0 | 0.53 x 0.52 |
| 26 | pastille/cercle (numero ou icone) | 9.03, 5.0 | 0.53 x 0.52 |
| 25 | contenu | 0.96, 5.64 | 3.35 x 1.08 |
| 31 | contenu | 4.99, 5.64 | 3.35 x 1.08 |
| 28 | contenu | 9.03, 5.64 | 3.35 x 1.08 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [19] 1_Boxed - 2 columns X4

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 33 | sous-titre de colonne | 0.76, 2.51 | 5.71 x 0.76 |
| 34 | sous-titre de colonne | 6.86, 2.51 | 5.71 x 0.76 |
| 16 | sous-titre de colonne | 0.76, 3.32 | 5.71 x 0.81 |
| 25 | sous-titre de colonne | 6.86, 3.32 | 5.71 x 0.81 |
| 18 | sous-titre de colonne | 0.88, 3.43 | 2.01 x 0.58 |
| 26 | sous-titre de colonne | 6.98, 3.43 | 2.01 x 0.58 |
| 19 | sous-titre de colonne | 0.76, 4.17 | 5.71 x 0.81 |
| 27 | sous-titre de colonne | 6.86, 4.17 | 5.71 x 0.81 |
| 20 | sous-titre de colonne | 0.88, 4.28 | 2.01 x 0.58 |
| 28 | sous-titre de colonne | 6.98, 4.28 | 2.01 x 0.58 |
| 21 | sous-titre de colonne | 0.76, 5.02 | 5.71 x 0.81 |
| 29 | sous-titre de colonne | 6.86, 5.02 | 5.71 x 0.81 |
| 22 | sous-titre de colonne | 0.88, 5.13 | 2.01 x 0.58 |
| 30 | sous-titre de colonne | 6.98, 5.13 | 2.01 x 0.58 |
| 23 | sous-titre de colonne | 0.76, 5.87 | 5.71 x 0.81 |
| 31 | sous-titre de colonne | 6.86, 5.87 | 5.71 x 0.81 |
| 24 | sous-titre de colonne | 0.88, 5.98 | 2.01 x 0.58 |
| 32 | sous-titre de colonne | 6.98, 5.98 | 2.01 x 0.58 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [20] Circles - 2 columns
*Éléments parallèles : **2***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [23, 24, 25]
2. idx [26, 27, 28]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | pastille/cercle (numero ou icone) | 2.67, 2.81 | 1.97 x 1.97 |
| 26 | pastille/cercle (numero ou icone) | 8.7, 2.81 | 1.97 x 1.97 |
| 24 | sous-titre de colonne | 1.98, 4.87 | 3.35 x 0.68 |
| 27 | sous-titre de colonne | 8.01, 4.87 | 3.35 x 0.68 |
| 25 | contenu | 1.98, 5.63 | 3.35 x 1.14 |
| 28 | contenu | 8.01, 5.63 | 3.35 x 1.14 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [21] Circles - 3 columns
*Éléments parallèles : **3***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [23, 24, 25]
2. idx [20, 21, 22]
3. idx [26, 27, 28]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | pastille/cercle (numero ou icone) | 1.45, 2.81 | 1.97 x 1.97 |
| 20 | pastille/cercle (numero ou icone) | 5.68, 2.81 | 1.97 x 1.97 |
| 26 | pastille/cercle (numero ou icone) | 9.91, 2.81 | 1.97 x 1.97 |
| 24 | sous-titre de colonne | 0.76, 4.87 | 3.35 x 0.68 |
| 21 | sous-titre de colonne | 4.99, 4.87 | 3.35 x 0.68 |
| 27 | sous-titre de colonne | 9.23, 4.87 | 3.35 x 0.68 |
| 25 | contenu | 0.76, 5.63 | 3.35 x 1.14 |
| 22 | contenu | 4.99, 5.63 | 3.35 x 1.14 |
| 28 | contenu | 9.23, 5.63 | 3.35 x 1.14 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [22] Circles - 4 columns
*Éléments parallèles : **4***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [23, 24, 25]
2. idx [29, 30, 31]
3. idx [32, 33, 34]
4. idx [26, 27, 28]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | pastille/cercle (numero ou icone) | 1.15, 2.81 | 1.97 x 1.97 |
| 29 | pastille/cercle (numero ou icone) | 4.18, 2.81 | 1.97 x 1.97 |
| 32 | pastille/cercle (numero ou icone) | 7.19, 2.81 | 1.97 x 1.97 |
| 26 | pastille/cercle (numero ou icone) | 10.21, 2.81 | 1.97 x 1.97 |
| 24 | sous-titre de colonne | 0.76, 4.87 | 2.76 x 0.68 |
| 30 | sous-titre de colonne | 3.78, 4.87 | 2.76 x 0.68 |
| 33 | sous-titre de colonne | 6.8, 4.87 | 2.76 x 0.68 |
| 27 | sous-titre de colonne | 9.82, 4.87 | 2.76 x 0.68 |
| 25 | contenu | 0.76, 5.63 | 2.76 x 1.14 |
| 31 | contenu | 3.78, 5.63 | 2.76 x 1.14 |
| 34 | contenu | 6.8, 5.63 | 2.76 x 1.14 |
| 28 | contenu | 9.82, 5.63 | 2.76 x 1.14 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [23] Circles - 2 columns X2
*Éléments parallèles : **4***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [23, 24, 25]
2. idx [29, 30, 31]
3. idx [26, 27, 28]
4. idx [32, 33, 34]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 0.93 |
| 23 | pastille/cercle (numero ou icone) | 0.76, 2.81 | 1.66 x 1.66 |
| 24 | sous-titre de colonne | 2.63, 2.81 | 3.71 x 0.68 |
| 29 | pastille/cercle (numero ou icone) | 6.98, 2.81 | 1.66 x 1.66 |
| 30 | sous-titre de colonne | 8.85, 2.81 | 3.71 x 0.68 |
| 25 | contenu | 2.63, 3.5 | 3.71 x 0.97 |
| 31 | contenu | 8.85, 3.5 | 3.71 x 0.97 |
| 26 | pastille/cercle (numero ou icone) | 0.77, 4.85 | 1.66 x 1.66 |
| 27 | sous-titre de colonne | 2.64, 4.85 | 3.71 x 0.68 |
| 32 | pastille/cercle (numero ou icone) | 6.99, 4.85 | 1.66 x 1.66 |
| 33 | sous-titre de colonne | 8.86, 4.85 | 3.71 x 0.68 |
| 28 | contenu | 2.64, 5.53 | 3.71 x 0.97 |
| 34 | contenu | 8.86, 5.53 | 3.71 x 0.97 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [24] Design - Circle left

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 14 | contenu | 6.67, 0.71 | 5.91 x 6.09 |
| 13 | capsule | 0.76, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 4.26 x 2.27 |
| 25 | contenu | 0.76, 3.75 | 4.26 x 2.55 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [25] Design - Arrow down

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 4.8, 0.82 | 3.74 x 0.47 |
| 0 | titre | 0.76, 1.48 | 11.81 x 1.39 |
| 25 | contenu | 0.76, 2.88 | 11.81 x 2.55 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [26] 3_Circles - 2 columns X2

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 13 | capsule | 0.76, 1.36 | 3.74 x 0.47 |
| 0 | titre | 0.76, 2.02 | 9.57 x 1.39 |
| 25 | contenu | 0.76, 3.42 | 9.57 x 2.55 |
| 10 | numero_slide | 0.76, 6.95 | 3.0 x 0.4 |

### [27] Disposition personnalisée
*Éléments parallèles : **1***

**Ordre visuel (gauche→droite, haut→bas)** — `[pastille, titre, texte]` :

1. idx [12, 11]

| idx | rôle | pos (in) | taille (in) |
|---|---|---|---|
| 12 | pastille/cercle (numero ou icone) | 3.83, 2.31 | 1.88 x 1.88 |
| 11 | contenu | 4.66, 2.31 | 4.83 x 1.88 |
