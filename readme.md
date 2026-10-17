# Dashboard des cartes eSIM

**Dashboard en ligne : https://patsymn.github.io/MYBESTSIM/**

## Organisation du projet

```
.github/workflows/update-dashboard.yml   mise à jour automatique (GitHub Action)
dataset/                                 les 18 CSV des fournisseurs
invalid_dataset/                         fichiers volontairement cassés, pour les tests
docs/index.html                          le dashboard généré (publié par GitHub Pages)
src/read_data.py                         lire et valider les CSV
src/stats.py                             calculer les statistiques
src/dashboard.py                         générer la page HTML
```

## Statistiques bonus

Les six statistiques demandées décrivent le contenu du catalogue. J'en ai ajouté
trois pour répondre à la question suivante, celle d'un acheteur ou d'un
responsable produit : « qu'est-ce qui est une bonne affaire ? ».

**7. Prix moyen par fournisseur.** Les questions 5 et 6 donnent un prix moyen
global et le nombre de cartes par fournisseur, mais pas qui est le moins cher.
Cette statistique classe les 18 fournisseurs (de 24,26 € pour 4S eSIM à 32,10 €
pour Yesim).
Limite :les catalogues ne sont pas comparables (volumes, durées et
zones différents), donc un écart d'environ 8 € se lit avec prudence.

**8. Prix par Go et par fournisseur.** Les questions 4 et 5 laissent deviner un
prix par Go, mais diviser directement le prix moyen par la data moyenne est
trompeur : le prix moyen inclut les 653 illimités, pas la data moyenne
(on obtiendrait environ 2,02 €/Go). J'ai donc calculé, pour chaque fournisseur,
le total des prix divisé par le total des Go, sur les forfaits limités
uniquement. Cette statistique corrige la précédente.
Limite : la durée de validité n'est pas prise en compte (1 Go sur 7 jours compte comme 1 Go sur 30 jours).

**9. Disponibilité par pays.** Elle répond à la question d'un voyageur : « que
puis-je acheter pour le pays où je vais ? ». Pour chaque pays : nombre de cartes,
nombre de fournisseurs, prix le plus bas, meilleur prix au Go, nombre de cartes
illimitées et prix de la moins chère. Les forfaits limités et illimités sont
présentés séparément, car un illimité n'a pas de prix au Go.

Limites :
- Europe, Asie, Monde et Amérique du Nord sont des cartes qui couvrent plusieurs
  pays. Elles ont leur propre ligne et ne sont pas ajoutées aux lignes des pays
  (par exemple, les cartes « Europe » ne sont pas comptées dans l'Espagne), car
  les données ne précisent pas quels pays chaque zone couvre. Une table
  pays-zones serait possible, mais elle reposerait sur des hypothèses que les
  données ne confirment pas.
- Le meilleur prix au Go vient presque toujours d'un gros forfait (50 Go) : ce
  chiffre compare les pays, il ne dit pas quelle carte acheter. Pour choisir, il
  faudrait connaître la durée du séjour et la consommation en Go du voyageur.
  Les données ne contiennent que la durée de validité de chaque carte (7, 15 ou
  30 jours).

## Quand les CSV changent

L'énoncé parle d'un import quotidien. Voici comment c'est géré.

**Le programme ne dépend pas du contenu des fichiers**
- Aucun nom de fichier n'est écrit dans le code : `Path('dataset').glob('*.csv')`
  lit tous les CSV du dossier. Un 19e fournisseur serait pris en compte sans
  modifier le code.
- Aucun chiffre n'est écrit à la main : tout est recalculé à chaque exécution
  (total, moyennes, classements, tableau par pays).

**Les fichiers invalides ne faussent pas les résultats**
- Un fichier avec un prix ou une durée illisible, une ligne trop courte, un fichier
  vide ou un fichier sans produit est **ignoré en entier**, avec un message
  d'avertissement. Les lignes lues avant l'erreur ne sont pas gardées : chaque
  fichier est d'abord lu dans une liste temporaire, ajoutée au résultat seulement
  si la lecture est complète.
- Un dossier introuvable ou sans CSV arrête le programme avec un message clair,
  au lieu d'afficher « 0 carte » en silence.
- Les cinq cas sont testés avec les fichiers du dossier `invalid_dataset/`.

**La page est régénérée automatiquement**
Une GitHub Action (`.github/workflows/update-dashboard.yml`) relance le programme
puis republie la page. Elle se déclenche :
- tous les jours à 6 h UTC ;
- à chaque `git push` qui modifie `dataset/` ou `src/` ;
- à la demande, avec le bouton « Run workflow » de l'onglet Actions.

Le lien du dashboard reste le même, seuls les chiffres changent. L'Action est
gratuite pour ce usage (quelques secondes d'exécution par jour).

**Hypothèse retenue**
Le dashboard est une page statique régénérée à chaque import, et non un serveur
qui relit les fichiers à chaque visite. C'est plus simple et plus fiable à
héberger (aucun serveur à maintenir). Un serveur serait une évolution possible.

## Choix de lecture des données

- **`None` plutôt que `0`** pour les forfaits illimités, afin de ne pas fausser
  les moyennes.
- **`top_up` gardé en texte** (« oui » / « non »), tel que fourni par les
  fournisseurs.
- **8 colonnes sur 12 chargées** : `product_name`, `country_code`, `data_display` et
  `currency` sont redondants avec d'autres colonnes ou constants.
- **Le code `NA` est lu comme du texte**, pas comme une valeur manquante (c'est le
  piège de pandas, qui n'est pas utilisé ici).
- **Les offres qui se ressemblent ne sont pas fusionnées** : plusieurs cartes du même
  fournisseur partagent pays, volume et durée, mais chaque SKU est unique, donc
  une ligne = une carte.

## Limites connues

- **Les colonnes sont lues par leur position** : si un fournisseur change l'ordre
  de ses colonnes, la lecture serait fausse sans erreur visible.
- **Les fichiers rejetés ne sont signalés que dans le terminal** (ou le journal de
  l'Action) : la page ne les affiche pas encore.
- **Les CSV doivent être dans le dépôt** pour que l'Action puisse les lire. En
  production, ils viendraient d'un dossier partagé, d'un stockage en ligne ou d'une
  API, et l'Action les récupérerait avant de lancer le programme.
- La durée de validité est ignorée dans le prix par Go, et les zones ne sont pas
  rattachées aux pays (voir plus haut).

## Méthodologie et utilisation de l'IA

J'ai utilisé Claude (Anthropic) comme tuteur et comme assistant de code. Pour
être précise sur la répartition :

**Ce que j'ai fait moi-même**
- Exploré les fichiers CSV : colonnes, séparateur, encodage, valeurs vides.
- Planifié le projet par étapes (lire, calculer, afficher) et choisi l'organisation en fichiers, avec une seule responsabilité par fichier.
- Écrit la lecture des CSV à partir d'un code de mon précédent projet
  (`csv.reader`, `try/except`), puis l'ai adaptée à ces données et testée.
- Pris les décisions de lecture : `None` pour les illimités, `top_up` en texte.
- Choisi les statistiques bonus et décidé de comment présenter leurs limites.
-  Mis en place le déploiement (GitHub Pages et GitHub Action).

**Ce que l'IA m'a apporté**
- Les valeurs de référence que j'ai utilisées pour vérifier mon résultat, et les fichiers corrompus du dossier `invalid_dataset/`.
- Une grande partie du code de `stats.py` et de `dashboard.py.
- Rédaction et correction du README.
- Réflexion sur l’automatisation : page statique ou dynamique, ce qui se passe quand les CSV changent chaque jour, arbitrages coût et simplicité.
- Aide au débogage.


