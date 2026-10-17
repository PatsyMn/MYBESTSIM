## Méthodologie et utilisation de l'IA

- J'ai d'abord exploré moi-même les fichiers CSV : colonnes, séparateur,
  encodage, valeurs vides. Claude m'a aidée à repérer des pièges (`data_gb`
  vide pour les produits « Illimité », code pays `NA` pour l'Amérique du Nord).
- J'ai planifié le projet par étapes et je l'ai
  organisé en fichiers distincts, avec une seule responsabilité par fichier.
- Je suis partie d'un code de lecture issu d'un précédent projet (`csv.reader`,
  `try/except`) et je l'ai adapté à ces données, avec les retours de Claude.

**Ce que l'IA m'a apporté**
- Des valeurs de référence (5 056 produits, 653 forfaits illimités) que j'ai
  utilisées pour vérifier mon résultat.
- La génération des petits fichiers corrompus du dossier `invalid_dataset/`.


## Statistiques bonus

Les six statistiques demandées décrivent le contenu du catalogue. J'en ai ajouté
trois pour répondre à la question suivante, celle d'un acheteur ou d'un
responsable produit : « qu'est-ce qui est une bonne affaire ? ».

**7. Prix moyen par fournisseur**
Les questions 5 et 6 donnent un prix moyen global et le nombre de cartes par
fournisseur, mais pas qui est le moins cher. Cette statistique classe les 18
fournisseurs par prix moyen (de 24,26 € pour 4S eSIM à 32,10 € pour Yesim).
Limite : les catalogues ne sont pas comparables (volumes, durées et zones
différents), donc un écart d'environ 8 € se lit avec prudence.

**8. Prix par Go et par fournisseur**
Un Go coûte-t-il plus cher chez certains fournisseurs ? Pour le savoir, je
divise le total des prix par le total des Go de chaque fournisseur.

Je ne garde que les forfaits avec un volume : un forfait illimité n'a pas de
nombre de Go, donc il est exclu du calcul (comme pour la question 4).

Résultat : un Go coûte entre 1,63 € (Ubigi, GigSky, Yatelo) et 1,88 € (4S eSIM).

Cette statistique corrige la précédente : 4S eSIM est le moins cher par carte
(24,26 €), mais le plus cher au Go. Ses cartes ont moins de data (10,3 Go en
moyenne, contre 15,7 Go chez Ubigi), donc un prix bas ne veut pas dire un bon
prix par Go.

Limite : la durée n'est pas prise en compte. 1 Go valable 7 jours et 1 Go
valable 30 jours comptent pareil.

**9. Disponibilité par pays**
Cette statistique répond à la question d'un voyageur : « que puis-je acheter
pour le pays où je vais ? ». Pour chaque pays : nombre de cartes, nombre de
fournisseurs, prix le plus bas, meilleur prix au Go, nombre de cartes illimitées
et prix de la moins chère. Les forfaits limités et illimités sont présentés
séparément, car ils ne se comparent pas de la même façon (un illimité n'a pas
de prix au Go).
Limites : les 4 zones (Europe, Asie, Monde, Amérique du Nord) sont des lignes à
part, car les données n'indiquent pas quels pays elles couvrent.
le meilleur prix au Go vient presque toujours d'un gros forfait
(50 Go), car plus le forfait est gros, moins le Go est cher. Ce chiffre
compare donc les pays, mais ne dit pas quelle carte acheter. Pour choisir, il
faudrait connaître le voyage de la personne : combien de jours elle reste, et
combien de Go elle consomme. Nos données ne contiennent que la durée de
validité de chaque carte (7, 15 ou 30 jours), pas la durée du séjour. Un
voyageur qui reste 3 jours avec 1 Go n'a pas besoin d'une carte de 50 Go
valable 30 jours.
