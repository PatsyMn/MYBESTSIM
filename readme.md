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
