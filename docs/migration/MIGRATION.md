# Civis — Documentation de migration

**Statut :** référence unique du chantier de refonte de l'interface.
**Portée :** `web/` principalement, avec deux dépendances identifiées hors périmètre (`pipeline/`, `content/`).
**Public :** toute session de développement, y compris une session sans aucun contexte antérieur.

> **Règle d'usage.** Une PR s'implémente en lisant `docs/migration/PR-XX.md` et, si nécessaire, `INVARIANTS.md` et `DECISIONS.md`. Le présent document donne le cadre général ; il n'est pas nécessaire de le lire intégralement pour implémenter une PR isolée.

---

## Table des matières

1. [Objectif global](#1-objectif-global)
2. [Philosophie du chantier](#2-philosophie-du-chantier)
3. [Contexte actuel du projet](#3-contexte-actuel-du-projet)
4. [Architecture existante](#4-architecture-existante)
5. [Architecture cible](#5-architecture-cible)
6. [État du front-end](#6-état-du-front-end)
7. [État du pipeline](#7-état-du-pipeline)
8. [État des contenus](#8-état-des-contenus)
9. [État de l'API](#9-état-de-lapi)
10. [Dette technique actuelle](#10-dette-technique-actuelle)
11. [Raisons de la migration](#11-raisons-de-la-migration)
12. [Les dix principes P1–P10](#12-les-dix-principes-p1p10)
13. [Décisions produit actées](#13-décisions-produit-actées)
14. [Décisions techniques actées](#14-décisions-techniques-actées)
15. [Contraintes de conception](#15-contraintes-de-conception)
16. [Contraintes d'accessibilité](#16-contraintes-daccessibilité)
17. [Contraintes de sécurité](#17-contraintes-de-sécurité)
18. [Contraintes de performance](#18-contraintes-de-performance)
19. [Contraintes de maintenabilité](#19-contraintes-de-maintenabilité)
20. [Contraintes de réversibilité](#20-contraintes-de-réversibilité)
21. [Contraintes de revue](#21-contraintes-de-revue)
22. [Invariants absolus](#22-invariants-absolus)
23. [Hors périmètre](#23-hors-périmètre)
24. [Dépendances entre PR](#24-dépendances-entre-pr)
25. [Stratégie de migration incrémentale](#25-stratégie-de-migration-incrémentale)
26. [Pourquoi ce découpage](#26-pourquoi-ce-découpage)
27. [Stratégie de validation](#27-stratégie-de-validation)
28. [Stratégie de tests](#28-stratégie-de-tests)
29. [Stratégie de rollback](#29-stratégie-de-rollback)
30. [Glossaire](#30-glossaire)
31. [Manques documentés hors périmètre `web/`](#31-manques-documentés-hors-périmètre-web)

---

## 1. Objectif global

Faire passer l'interface de Civis d'un état **fonctionnel mais muet** à un état où **les propriétés qui rendent le projet digne de confiance sont observables par l'utilisateur**.

Le produit fonctionne déjà : le questionnaire aveugle, le scoring côté client, la révélation et les compteurs anonymes sont opérationnels. Ce qui manque n'est pas de la fonctionnalité mais de la **manifestation** : la datation du corpus, le statut éditorial des énoncés, la couverture réelle des programmes, les limites du score, la provenance logicielle, le mode de fabrication des questions — tout cela existe dans le dépôt et n'atteint jamais l'utilisateur.

La migration n'ajoute donc presque aucune fonctionnalité. Elle **rend visible ce qui est déjà vrai**, corrige trois défauts d'intégrité de l'instrument lui-même (option pré-cochée, échelle qui se replie, score sans dénominateur) et supprime plus de code qu'elle n'en ajoute côté logique.

**Trois objectifs mesurables :**

1. Aucune affirmation affichée sans moyen de la contredire.
2. Aucun nombre affiché sans sa base de calcul.
3. Aucun invariant du projet cassable sans qu'un test échoue.

---

## 2. Philosophie du chantier

> Les affirmations ne valent rien. Les preuves valent tout.

Cette phrase gouverne l'ensemble du chantier et se traduit en trois règles de travail :

**On ne remplace pas une garantie par une intention.** Quand une contrainte peut être vérifiée par une machine, elle doit l'être. Le dépôt applique déjà ce principe au contenu (`pipeline.check` vérifie chaque citation mot pour mot). La migration l'étend à l'interface : aveuglement, contrastes, jetons deviennent des tests.

**On ne dissimule pas les défauts, on les affiche.** Le corpus est déséquilibré (4 propositions pour une formation, 19 pour une autre), le score est structurellement sensible à cette couverture, l'échantillon statistique est auto-sélectionné, les questions sont nos reformulations rédigées avec l'aide d'un modèle de langage. Chacun de ces faits est publié dans le dépôt. Le chantier consiste largement à les faire remonter dans l'interface, **avant qu'un tiers ne les découvre**.

**On préfère retirer.** Le pourcentage, la barre de progression, le classement, le rendu par concaténation de chaînes, l'échappement manuel : la refonte les supprime. Un élément ne survit que s'il informe. S'il ne fait que retenir l'utilisateur ou embellir la page, il sort.

---

## 3. Contexte actuel du projet

Civis est un questionnaire politique à l'aveugle. Des propositions issues de programmes officiels sont présentées **sans attribution** ; l'utilisateur se positionne ; l'affiliation n'est révélée qu'à la fin.

L'objectif n'est pas de mesurer une opinion mais de **supprimer le biais d'appartenance** : on retire l'étiquette pendant que l'utilisateur se positionne. Ce n'est pas un sondage.

Le projet est un site **Astro statique** publié sur GitHub Pages, accompagné d'un service de compteurs anonymes optionnel en Rust, et d'un pipeline Python de récolte et de vérification des documents.

**Hypothèses considérées comme vraies dans toute cette documentation :**

- Le dépôt est maintenu par **une seule personne**. Toute solution dont le coût de maintenance dépasse le gain est rejetée par défaut.
- Le site doit rester **entièrement fonctionnel sans le service de compteurs**. Sans lui, seule la section d'agrégats disparaît, et avec elle la case d'opt-out.
- Le jeu de données actuel repose sur des **documents de 2024** (législatives, pages de programme officielles), les programmes 2027 n'étant pas publiés.
- Aucun appel à un modèle de langage n'a lieu à l'exécution du site.

---

## 4. Architecture existante

```
content/    JSON versionné : sources/ (empreintes sha256), programs/, questions/
pipeline/   Python — fetch, empreintes, extraction, génération LLM hors ligne
web/        Astro statique, i18n fr/en, scoring intégralement côté client
api/        Rust + axum + SQLite, deux endpoints de compteurs
```

**Git est la base de données** des questions, programmes et empreintes. **SQLite ne contient que des entiers.** Si la base disparaît, on perd des statistiques, jamais le produit.

Chaîne de build (`.github/workflows/pages.yml`, poussée sur `main`) :

```
checkout → setup-node 22 → npm ci (web/)
        → setup-python 3.12 → pip install -r pipeline/requirements.txt
        → python -m pipeline.run --election fr-2027 --step fetch
        → python -m pipeline.check
        → npm test (web/)
        → npm run build (web/)
        → upload-pages-artifact (web/dist) → deploy-pages
```

Seule variable injectée au build : `PUBLIC_CIVIS_API` (variable de dépôt, vide par défaut).

`web/astro.config.mjs` : `output: "static"`, `site: "https://vianpyro.github.io"`, `base: "/Civis"`, `redirects: { "/": "/Civis/fr/" }`, `vite.server.fs.allow: [".."]` (permet d'importer `content/` depuis `web/`).

---

## 5. Architecture cible

Aucun changement d'architecture générale. Le chantier est **intra-`web/`**, avec deux exceptions documentées.

```
web/src/
  components/     ← CRÉÉ : voir le tableau d'attribution ci-dessous
  layouts/        ← Base.astro, modifié (appareil de version, correctifs)
  lib/            ← score.js étendu, ui.js restructuré, paths.js inchangé
  pages/[lang]/   ← index.astro (questionnaire), results.astro,
                     + page de méthodologie (PR-13)
  styles.css      ← CONSERVÉ à cet emplacement, restructuré (PR-03)
  <jetons>.css    ← CRÉÉ (PR-03), importé par styles.css, à côté de styles.css
  *.test.mjs      ← tests de jetons, de contraste, de score
```

> **`styles.css` n'est jamais déplacé.** Il reste `web/src/styles.css`. Toutes les listes
> « fichiers concernés » et « fichiers interdits » des PR-02 à PR-14 désignent ce chemin exact ;
> un déplacement les rendrait toutes fausses et rendrait les interdits inopposables.
> Le fichier de jetons est créé **à côté**, pas dans un nouveau répertoire (DT-03).

### Attribution des composants

Un composant est créé **par la PR qui l'utilise en premier**, jamais « pour plus tard » (DT-06).

| Composant | Créé par | Utilisé par |
|---|---|---|
| Question | PR-05 | questionnaire |
| Échelle de réponse | PR-05 | questionnaire |
| Bandeau de restauration | PR-08 | questionnaire |
| Bloc de fin | PR-09 | questionnaire |
| Citation | **PR-10** | résultats |
| Source | **PR-10** | résultats |
| Résultat | **PR-10**, étendu par PR-11 | résultats |
| Statistique | PR-12 | résultats |
| Portée | PR-11 (premier usage) | résultats, méthodologie |
| Encart méthodologique | PR-13 | méthodologie |
| Étiquette de registre | PR-14 | résultats |
| Appareil de version | PR-02 (dans `Base.astro`, sans composant dédié) | toutes les pages |

**PR-05 ne crée que les deux composants du questionnaire** (Question, Échelle). Elle ne touche pas
`results.astro` : le balisage des résultats n'y existe pas comme balisage mais comme gabarits de
chaînes JavaScript, et l'extraire changerait la sortie compilée, ce que le critère octet à octet de
PR-05 interdit. Voir PR-05 « Pourquoi `results.astro` est hors périmètre ».

Exceptions hors `web/` :

| Fichier | PR | Motif |
|---|---|---|
| `.github/workflows/pages.yml` | PR-01, PR-02 | Étape de contrôle d'aveuglement ; injection du SHA de commit et de la date de build |
| `web/package.json` | PR-01 | Ajout d'un script de contrôle |
| `pipeline/fetch.py`, `content/sources/*/sources.json` | **hors des 14 PR** | Date de récolte absente du schéma — voir [OQ-03](#31-manques-documentés-hors-périmètre-web) |

---

## 6. État du front-end

Le front tient en **9 fichiers versionnés**, environ 600 lignes.

| Fichier | Lignes | Rôle |
|---|---|---|
| `web/src/pages/[lang]/index.astro` | 117 | Questionnaire : rendu + script client de soumission |
| `web/src/pages/[lang]/results.astro` | 189 | Révélation : aplatissement au build, **rendu intégral en JS** |
| `web/src/layouts/Base.astro` | 33 | Document HTML, lien d'évitement, sélecteur de langue |
| `web/src/styles.css` | 203 | Feuille unique, tous les styles |
| `web/src/lib/ui.js` | 86 | `LANGS`, `CHOICE_LABELS`, `THEMES`, `T` |
| `web/src/lib/score.js` | 44 | `score()`, `CHOICES`, `choiceIndex()` |
| `web/src/lib/score.test.mjs` | 59 | 7 tests `node:test` |
| `web/src/lib/paths.js` | 18 | `BASE`, `href()`, `API` |
| `web/astro.config.mjs` | 23 | Configuration de build |

**Il n'existe aucun répertoire `components/`.** Les deux pages portent tout le balisage.

**Dépendances :** `astro@^5.6.1`, seule et unique. Aucun préprocesseur, aucun framework de composants, aucune police distante, aucun script tiers. `npm test` = `node --test`, sans harnais.

### Jetons existants

Sept propriétés personnalisées dans `:root`, redéfinies sous `@media (prefers-color-scheme: dark)` :
`--bg`, `--fg`, `--muted`, `--line`, `--accent`, `--focus`, plus `color-scheme: light dark`.

Nommage **par support** (`bg`, `fg`, `line`) et non par intention (`primary`, `danger`) : c'est déjà conforme au système d'interface cible. Le socle est réutilisable.

Non jetonisé aujourd'hui : toutes les tailles de police (`1.9rem`, `1.25rem`, `1.05rem`, `.92rem`, `.9rem`, `.78rem`), tous les espacements (onze valeurs distinctes), les rayons (`8px`, `6px`, `999px`), les épaisseurs, la mesure (`44rem`), la pile de polices.

### Contrastes mesurés sur les jetons actuels

| Paire | Clair | Sombre | Seuil requis | Verdict |
|---|---|---|---|---|
| `--fg` / `--bg` | 16,64:1 | 16,09:1 | 7:1 (cible) | conforme |
| `--muted` / `--bg` | 6,39:1 | 7,11:1 | 7:1 (cible) | **clair non conforme** |
| `--line` / `--bg` | **1,37:1** | **1,46:1** | 3:1 (affordance) | **échec net** |
| `--focus` / `--bg` | 4,95:1 | 7,25:1 | 3:1 | conforme |

`--line` porte l'affordance des 180 contrôles du questionnaire. C'est le défaut d'accessibilité le plus grave du produit actuel.

### Couplage CSS ↔ balisage

La feuille cible massivement des **éléments** (`body`, `h1`, `h2`, `p`, `a`, `button`, `blockquote`, `details`, `summary`, `fieldset.question legend`) et huit classes (`.muted`, `.tagline`, `.theme`, `.choices`, `.bar`, `.result`, `.sticky`, `.skip-link`, `nav.langs`).

**Conséquence :** une refonte du balisage casse silencieusement les sélecteurs correspondants, sans qu'aucun test ne le détecte. C'est le premier risque de régression du chantier et il justifie l'ordre des PR.

Deux dépendances CSS notables :
- `.choices label:has(input:checked)` — le sélecteur `:has()` porte l'état sélectionné, sans repli. Exigence de base assumée.
- `color-mix(in srgb, var(--accent) 10%, transparent)` — valeur calculée hors jetons ; disparaît en PR-03.

---

## 7. État du pipeline

`pipeline/` (Python) : `fetch.py`, `extract.py`, `generate.py`, `check.py`, `run.py`.

`pipeline/check.py` applique les invariants de contenu en CI. Le contrôle porteur est la **vérification des citations** : chaque citation de `content/programs/` doit apparaître **mot pour mot** dans le document que sa source déclare. C'est ce qui rend la neutralité vérifiable par une machine plutôt qu'affirmée dans un README.

Comportement notable et à préserver : hors ligne, cette vérification est **signalée comme sautée, jamais silencieusement validée**. C'est l'application de P8 côté pipeline, antérieure à la formalisation du principe.

`check.py` vérifie aussi les empreintes orphelines (`.sha256` sans entrée correspondante dans `sources.json`) et contient un ensemble `THEMES` en dur qui duplique le vocabulaire de `web/src/lib/ui.js` sans lien mécanique entre les deux.

**Le pipeline n'est pas modifié par les 14 PR.** Une modification y est identifiée mais laissée hors périmètre : voir [OQ-03](#31-manques-documentés-hors-périmètre-web).

---

## 8. État des contenus

### Schémas (vérifiés par lecture directe)

| Fichier | Schéma |
|---|---|
| `content/questions/fr-2027.json` | `{election, questions:[{id, theme, text:{fr,en}}]}` |
| `content/questions/fr-2027.positions.json` | `{questionId: [{point, stance}]}` — `stance` ∈ {−1, 1} |
| `content/programs/fr-2027/*.json` | `{election, party:{id,name,short}, source_id, points:[{id, theme, quote}]}` |
| `content/sources/fr-2027/sources.json` | `[{id, party, title, published, url}]` |
| `content/sources/fr-2027/*.sha256` | texte brut : `<empreinte>  <url>`, **hors JSON** |

**Absences structurantes :**
- Aucun champ de **version ou de date par question** → une reformulation ne laisse de trace que dans l'historique git.
- Aucune **ancre de page ou de section par citation** → la traçabilité s'arrête au document entier.
- Aucune **date de récolte** dans `sources.json` — seulement `published`.

### Métriques du corpus fr-2027 (mesurées)

- **30 questions**, ordonnées dans le fichier par thème :
  `economy ×5, social ×5, ecology ×5, institutions ×3, security ×4, health ×3, immigration ×3, europe ×2`
  (`education` existe dans `THEMES` mais n'est utilisé par aucune question.)
- **4 formations** : `nfp`, `ensemble`, `lr`, `rn`.
- **Couverture par formation** : `nfp` 19, `rn` 15, `ensemble` 10, **`lr` 4**.
- **Positions par question** : 1 formation ×14, 2 formations ×14, 3 formations ×2, jamais 4, jamais 0.
- **Polarité des positions** : `nfp` 15 « défend » / 4 « s'oppose » ; `rn` 13/2 ; `ensemble` 6/4 ; `lr` 2/2.
- Longueur moyenne d'un énoncé français : 89 caractères ; maximum : 120.

**Conséquences directes sur l'interface** (ce sont les faits qui motivent DP-10 à DP-13) :
1. Un score comparant 4 propositions à 19 n'est pas comparable ; l'afficher sans base est trompeur.
2. 14 questions sur 30 ne concernent qu'une seule formation : y répondre fait monter cette formation **sans rien retirer aux autres**. Le résultat est donc structurellement sensible à la couverture du corpus, indépendamment des opinions de l'utilisateur.
3. Le déséquilibre de polarité (`nfp` et `rn` majoritairement en « défend ») expose au biais d'acquiescement.

Ces trois faits doivent être **affichés spontanément** par le produit (P5, DP-13). Ils ne peuvent pas être corrigés par l'interface : leur correction relève de `pipeline/` et `content/`, hors périmètre.

---

## 9. État de l'API

`api/src/main.rs`, Rust + axum + SQLite. **Deux endpoints sur une route.**

| Route | Méthode | Entrée | Sortie |
|---|---|---|---|
| `/counts` | `POST` | `{question: String, choice: usize}` | `204` ou `400` |
| `/counts` | `GET` | — | `{questionId: [n0..n4]}` pour **toutes** les questions connues |

Table unique : `counts(question TEXT, choice INTEGER, n INTEGER, PRIMARY KEY(question, choice)) WITHOUT ROWID`. Aucune colonne permettant de rapprocher deux réponses. Aucun identifiant, aucune session, aucun horodatage.

Frontière de confiance (`valid()`) : `choice < 5` et `question` présente dans le fichier de questions chargé au démarrage. Sans ce contrôle, un attaquant ferait croître la table sans borne en inventant des identifiants.

`tally()` renvoie **toujours l'échelle complète**, y compris des zéros, et écarte les lignes hors échelle éventuellement présentes en base — la forme de la réponse est garantie côté serveur.

CORS ouvert : sans authentification ni données par utilisateur, une restriction d'origine ne protégerait rien.

**Conséquence décisive pour la migration :** l'effectif exigé par DP-15 est **déjà calculable côté client** — c'est la somme du tableau d'une question. **Aucune modification de l'API n'est nécessaire par les 14 PR.**

**Conséquence sur les libellés :** cet effectif est un nombre de **réponses par proposition**, jamais un nombre de personnes, que l'architecture rend structurellement inconnaissable. Tout libellé parlant de « participants » serait factuellement faux (DT-11).

---

## 10. Dette technique actuelle

### Composants difficiles à maintenir

**`results.astro` — 95 lignes de rendu par concaténation de chaînes** (lignes 95-189). Échappement manuel par une fonction maison `escape()` (lignes 103-107), HTML entremêlé à la logique, et rendu client d'un contenu **entièrement connu au build**. Toute évolution passe par l'édition de chaînes de gabarit sans aucune vérification. → PR-10.

**`index.astro` — le script client ignore `ui.js`.** N'ayant pas accès aux modules du frontmatter, il réécrit la pluralisation de la progression (lignes 80-84) alors que `T.progress()` existe (`ui.js:39`). Toute correction de formulation doit être faite deux fois. → PR-05, PR-09.

**`styles.css` — feuille unique couplée au balisage par sélecteurs d'éléments.** Atténué par PR-03 et PR-05, **non éliminé** : c'est un choix assumé pour un dépôt de cette taille. Des styles par composant coûteraient plus qu'ils ne rapporteraient.

### Duplications recensées

| Id | Duplication | Emplacements | Gravité |
|---|---|---|---|
| **D1** | L'échelle `[-1,-0.5,0,0.5,1]` écrite **trois fois** | `score.js:39` (exportée), `index.astro:94`, `results.astro:101` | Élevée |
| **D2** | Pluralisation de la progression réécrite | `ui.js:39` vs `index.astro:80-84` | Élevée |
| **D3** | Deux mécanismes de passage des chaînes au client | `data-*` dans `index.astro` vs île JSON dans `results.astro` | Moyenne |
| **D4** | Chaînes bilingues en dur | `Base.astro:19` et `:21` | Faible |
| **D5** | Vocabulaire des thèmes en double exemplaire non lié | `ui.js:8-31` et `pipeline/check.py` | Faible |
| **D6** | Attributs `style=` inline | `index.astro:50,55,63` ; `results.astro:124,127,151,176,180` | Moyenne |

### Incohérences

- L'échec silencieux de l'API est **documenté comme une qualité** dans un commentaire de `results.astro` (lignes 159-161) alors que le système d'interface l'interdit désormais. Le commentaire devra être corrigé en même temps que le comportement (PR-12), sinon le code documentera une règle abolie.
- `choiceIndex()` est exportée et testée mais **n'est utilisée nulle part** ; le besoin qu'elle couvre est réimplémenté ailleurs (D1).
- Le commentaire `api/src/main.rs:18` déclare que la largeur d'échelle est tenue en phase avec `score.js` — **aucun test ne le vérifie**, malgré des suites des deux côtés.
- `index.astro:76` filtre `key !== "aggregate"` dans `FormData`, mais la case a un `id` et **aucun attribut `name`** : elle n'entre jamais dans `FormData`. **Code mort trompeur.**

### Dépendances inutiles

**Aucune.** Le point important de cette section est prescriptif : **aucune dépendance ne doit être ajoutée par ce chantier** (DT-01). Ni pilote de navigateur, ni analyseur CSS, ni bibliothèque de composants, ni utilitaire d'audit d'accessibilité.

### Simplifications acquises par la migration

| Simplification | PR | Gain |
|---|---|---|
| Disparition de `escape()` et de tout `innerHTML` | PR-10 | ~15 lignes et une classe de vulnérabilité |
| Disparition du calcul de pourcentage et de la barre | PR-11 | Code et concept en moins |
| Consolidation de l'échelle en une seule définition | PR-10 | Trois copies → une |
| Suppression du garde mort sur `aggregate` | PR-04 | Code trompeur |
| Suppression de `color-mix` | PR-03 | Valeur calculée hors jetons |
| Barre de progression jamais construite | — | Évitée par DP-20 |

**Bilan attendu : la migration retire plus de lignes de logique qu'elle n'en ajoute.** Le volume croît en balisage statique et en contenu rédactionnel.

---

## 11. Raisons de la migration

Par gravité décroissante, avec le défaut constaté et la PR qui le traite.

| # | Défaut | Pourquoi c'est grave | PR |
|---|---|---|---|
| 1 | **L'option « Passer » est pré-cochée** sur les 30 questions (`index.astro:41`), avec le style d'état sélectionné | L'outil répond à la place de l'utilisateur sur un instrument politique. Le compteur affiche « 0 réponse » pendant que 30 options apparaissent cochées : deux éléments de l'interface se contredisent à l'écran | PR-04 |
| 2 | **Le score compare l'incomparable** : dénominateurs de 4 à 19, 14 questions mono-formation, formule ramenant tout modéré vers 50 % | C'est le risque existentiel du projet : un score aberrant en capture d'écran circule mieux qu'un README | PR-11 |
| 3 | **Bordure des contrôles à 1,37:1** | Échec WCAG 1.4.11 sur l'affordance de 180 contrôles. L'engagement d'accessibilité est pris dans le README sans être tenu | PR-03 |
| 4 | **L'échelle se replie sur 3-4 lignes en mobile** | Les positions 4 et 5 passent sous les positions 1 et 2 : l'axe cesse d'être un axe et les options rejetées en fin de ligne sont mécaniquement moins choisies. **Défaut de mesure, pas de mise en page** | PR-06 |
| 5 | **L'abandon détruit tout** : aucune persistance | Perdre le travail de quelqu'un est une atteinte à la confiance autant qu'à la complétion | PR-08 |
| 6 | **Le consentement est collé au bouton d'envoi**, son explication hors écran | Décision de vie privée prise au moment de l'impatience, séparée de son explication : le patron du bandeau cookies, au seul endroit où la sincérité est l'argument | PR-09 |
| 7 | **L'alerte de soumission est placée après la barre flottante** (`index.astro:64`) | Elle peut n'être jamais visible pour un utilisateur voyant | PR-04 |
| 8 | **La preuve est l'élément le mieux caché du produit** : citations et documents enfouis dans des `<details>` repliés | La citation sourcée est ce qui distingue Civis d'un quiz | PR-10, PR-13 |
| 9 | **Le site ne dit nulle part que les documents datent de 2024** | Information la plus susceptible de faire crier à la tromperie si découverte tardivement | **PR-07** (en-tête, DP-27), PR-13 |
| 10 | **Aucune provenance logicielle** : ni commit, ni date de build | Un instrument sans numéro de série n'est pas auditable | PR-02 |
| 11 | **Le rôle du modèle de langage n'est nulle part dans l'interface** | Honnêteté à deux étages : franche envers qui lit le code, silencieuse envers les autres | PR-13 |
| 12 | **L'échec du service de compteurs est silencieux** | Faire disparaître une section présente un état du monde différent du réel | PR-12 |
| 13 | **Aucun test ne protège l'invariant d'aveuglement** | C'est la seule erreur véritablement irrattrapable du chantier | PR-01 |

---

## 12. Les dix principes P1–P10

Ces principes sont **normatifs**. Une PR qui en viole un est rejetée avant tout examen de ses mérites.

**P1 — Toute affirmation affichée doit indiquer comment la contredire ; sinon elle est supprimée.**
Si l'on ne sait pas énoncer le geste précis qu'une personne accomplirait pour nous prendre en défaut, et ce qu'elle observerait, la phrase ne doit pas être écrite. La valeur d'une revendication falsifiable ne vient pas du nombre de gens qui la vérifient mais de son exposition à la réfutation : les adversaires du projet, eux, vérifieront. *Limite :* si l'invitation à vérifier devient un ornement, elle retombe dans la catégorie qu'elle prétendait quitter.

**P2 — Énoncer la revendication la plus étroite qui soit vraie, jamais la plus flatteuse.**
« Nous ne pouvons pas vous identifier » est indémontrable ; « la page du questionnaire ne contient aucune donnée de parti » est exact et observable. Corollaire : **le résidu non maîtrisé doit être écrit** (l'adresse IP vue par le serveur de compteurs, déjà signalée dans un commentaire de `index.astro:99-103`).

**P3 — Ce que nous avons écrit doit être visuellement séparé de ce que nous avons cité.**
L'utilisateur ne répond pas à une proposition de programme : il répond à **notre reformulation**, rédigée en question fermée, éventuellement traduite. Entre le document et l'énoncé, il y a une couche éditoriale dont la fidélité est le seul endroit où un biais peut s'introduire sans laisser de trace dans une empreinte. Conséquence : la nature de cette couche doit être déclarée, y compris le recours à un modèle de langage pour les brouillons.

**P4 — Aucun nombre ne s'affiche sans son dénominateur ni la composition de sa base.**
La base voyage avec la mesure, dans la même phrase et au même poids visuel. Une mesure dont on ne peut pas afficher la base ne doit pas être affichée.

**P5 — Les limites connues s'affichent au même niveau de visibilité que les résultats, et de notre propre initiative.**
Un défaut annoncé par l'instrument devient une caractéristique documentée ; le même défaut révélé par un opposant devient une preuve de duplicité. Les données étant publiques, il n'existe aucune autre stratégie disponible.

**P6 — L'instrument est daté, versionné et attribuable.**
Commit de construction, date, dates des documents sources, empreintes, responsable éditorial et déclaration d'intérêts. Une déclaration d'intérêts nominative est admissible malgré P1 parce qu'elle est *falsifiable par contradiction* : elle engage quelqu'un qui peut être démenti.

**P7 — Aucune information sur les autres participants avant que les réponses soient figées ; après, elle est présentée comme un échantillon, jamais comme une norme.**
La première moitié est l'invariant fondateur. La seconde encadre les agrégats : échantillon auto-sélectionné, puis filtré par le consentement — valeur épistémique faible, pouvoir de comparaison sociale fort.

**P8 — Une donnée absente s'affiche comme absente ; le silence n'est pas une option honnête.**
Trois états distincts : absence de service, absence de donnée, donnée nulle.

**P9 — Un élément d'interface a le droit d'informer, pas de modifier le comportement.**
Test littéral : *si cet élément était retiré, l'utilisateur serait-il moins informé, ou seulement moins susceptible d'aller au bout ?* Dans le second cas, il sort. Ce test élimine la barre de progression, les encouragements et l'avance automatique.

**P10 — Ce qui est vrai dans le dépôt doit être vrai dans l'interface.**
Cinq faits assumés par écrit dans le dépôt n'atteignent jamais l'utilisateur : documents de 2024, génération assistée par modèle de langage, déséquilibre de couverture, limite de l'adresse IP, nature auto-sélectionnée des statistiques. Une propriété est publiable et accessible depuis le produit, ou elle ne devrait pas non plus figurer dans un dépôt public.

---

## 13. Décisions produit actées

Registre complet et justifications détaillées : **`DECISIONS.md`**. Résumé opérationnel :

| Id | Décision | PR concernées |
|---|---|---|
| DP-01 | Aucune affiliation n'atteint le client avant la dernière réponse | PR-01 (garde-fou), toutes |
| DP-02 | Aucune statistique agrégée pendant le questionnaire | PR-12 |
| DP-03 | Aucun résultat individuel stocké ; incréments indépendants | PR-09 |
| DP-04 | Agrégation par défaut, opt-out — **maintenue** | PR-09 |
| DP-05 | Chaque question porte son document officiel et sa citation exacte | PR-10, PR-13 |
| DP-06 | Git = source de vérité ; SQLite = compteurs uniquement | — |
| DP-07 | **Pas de page d'accueil.** Le questionnaire est la page d'entrée | PR-07 (en-tête, DP-27), PR-13 |
| DP-08 | **Page unique**, pas de wizard | PR-06, PR-07 |
| DP-09 | Brouillon en `sessionStorage`, restauration signalée, **jamais `localStorage`** | PR-08 |
| DP-10 | Résultat en **fraction explicite** ; pas de pourcentage, pas de barre, pas de rang | PR-11 |
| DP-11 | **Niveau de confiance** qualitatif, plafonné, issu d'une règle publiée. **Bornes arrêtées** sur la base de comparaison : 0 → « aucune comparaison » · 1–4 → « très faible » · 5–9 → « faible » · ≥ 10 → « partielle » (plafond) | PR-11, PR-13 |
| DP-12 | **Couverture du corpus** toujours visible | PR-11 |
| DP-13 | Limites méthodologiques affichées spontanément | PR-11, PR-12, PR-13 |
| DP-14 | **Ordre des questions aléatoire** | PR-07, PR-13 |
| DP-15 | Agrégats maintenus sur la page de résultats, **qualifiés**. **Seuil arrêté** : pourcentages affichés seulement à partir de **100 réponses enregistrées pour la proposition** ; en deçà, effectifs bruts seuls | PR-12, PR-13 |
| DP-16 | Consentement opt-out avec **exposition littérale** de ce qui est envoyé | PR-09 |
| DP-17 | Rôle du modèle de langage documenté hors questionnaire, **4 faits dans l'ordre** | PR-13 |
| DP-18 | **Anglais = aide à la lecture** ; citations en langue d'origine ; 3 registres distinguables | PR-14 |
| DP-19 | Résultat calculé quel que soit le nombre de réponses, quantité comparée immédiatement visible | PR-11 |
| DP-20 | **Pas de barre de progression** | — (interdiction) |
| DP-21 | Animations limitées à une liste fermée | PR-03 |
| DP-22 | **Interface achromatique** : aucune couleur d'accent | PR-03 |
| DP-23 | Métadonnées de partage reléguées, **hors des 14 PR** | — |
| DP-24 | Pas de commutateur de thème manuel | PR-03 |
| DP-25 | Aucune pré-sélection, aucune avance automatique | PR-04, PR-06 |
| DP-26 | **Libellés de l'échelle : un jeu unique à toutes les largeurs.** FR « Pas du tout · Plutôt pas · Neutre · Plutôt oui · Tout à fait » · EN « Not at all · Rather not · Neutral · Rather yes · Fully agree ». Nom accessible = formulation complète. Maximum **7 caractères par mot** | PR-06, PR-13, PR-14 |
| DP-27 | **En-tête du questionnaire** : cinq énoncés au maximum, ≤ 120 caractères chacun, ordre fixé, plus un lien vers la méthodologie. **Porté par PR-07** | PR-07, PR-13 |
| DP-28 | **Bloc de provenance en tête des résultats** : une ligne par document source (titre, date de publication, empreinte, lien), registre appareil. **Porté par PR-11** | PR-10, PR-11, PR-13 |

---

## 14. Décisions techniques actées

| Id | Décision | Motif résumé |
|---|---|---|
| DT-01 | **Aucune nouvelle dépendance npm** | Mainteneur unique ; le coût de maintenance dépasserait le gain |
| DT-02 | Tests via `node --test` uniquement ; **pas de pilote de navigateur** | Idem ; la vérification navigateur est manuelle et normée (M1–M8) |
| DT-03 | Jetons dans un **fichier CSS dédié**, propriétés personnalisées natives | Pas d'étape de génération ; lisibles dans l'inspecteur, ce qui sert la vérifiabilité |
| DT-04 | Tests automatisés **de jetons** et **de contraste** | La contrainte est vérifiée, pas affirmée (P1) |
| DT-05 | Contrôle d'aveuglement **sur la sortie compilée**, après `npm run build` | Seule position qui résiste à un import ajouté par inadvertance |
| DT-06 | Extraction de composants en PR-05, **avant** les cinq PR qui modifient le questionnaire | Découplage des conflits, pas abstraction spéculative |
| DT-07 | Résultats **rendus en statique** ; JS résiduel de filtrage | 100 % des données sont connues au build |
| DT-08 | Permutation par **déplacement DOM** avant premier rendu | Un réordonnancement visuel CSS dissocierait ordre de focus et ordre visuel |
| DT-09 | **Ordre tiré persisté avec le brouillon**, même clé `sessionStorage` | Sinon la restauration reconstitue un questionnaire différent de celui affiché |
| DT-10 | **Aucune modification de l'API** | L'effectif est la somme du tableau renvoyé par `GET /counts` |
| DT-11 | Libellé « réponses par proposition », **jamais « participants »** | Le nombre de personnes est structurellement inconnaissable |
| DT-12 | Empreintes lues au build par **import brut** | `vite.server.fs.allow: [".."]` l'autorise déjà ; les `.sha256` ne sont pas du JSON |
| DT-13 | SHA de commit et date injectés au build ; **un build local est identifié comme tel** | Afficher un faux identifiant violerait P1 sur le composant censé le porter |
| DT-14 | Identifiant de page de la méthodologie : **`method`**, identique dans les deux langues | Prolonge le précédent du dépôt — la page de résultats porte déjà le slug anglais `results` — et INV-15. Évite une table de correspondance langue → slug pour une seule page |
| DT-15 | **PR-03 seule restructure `styles.css`** ; les suivantes n'y ajoutent que des blocs | Point de conflit Git unique |
| DT-16 | **PR-14 menée seule**, en fin de séquence | Elle restructure `T` et entre en conflit avec toute PR en vol |
| DT-17 | **Île JSON** comme mécanisme unique de passage des chaînes au client | Meilleur des deux mécanismes actuels : données structurées, échappement correct |
| DT-18 | `CHOICES` consommé depuis `score.js` ; **source unique** | Résout D1 |
| DT-19 | `:has()` requis, **sans repli** | Déjà le cas aujourd'hui ; exigence de base assumée |
| DT-20 | **Protocoles de comparaison explicites** pour les PR qui se prétendent neutres : HTML compilé octet à octet pour **PR-03** et **PR-05** ; texte rendu extrait du DOM final et ordres, sur trois jeux de réponses, pour **PR-10** | Seul critère acceptable pour une refactorisation neutre. **Aucune différence n'est justifiable** — une échappatoire subjective rendrait le critère inopposable |

---

## 15. Contraintes de conception

Référence complète : le système d'interface. Extrait opérationnel, contraignant pour toutes les PR.

**Palette.** Achromatique intégrale. Jetons : `paper`, `ink`, `ink-quiet`, `rule`, `edge`, `paper-inverse`. Valeurs proposées — **à revérifier par le test de contraste, jamais à affirmer sans mesure (P1)** :

| Jeton | Clair | Sombre | Contrainte |
|---|---|---|---|
| `paper` | `#FBFBF9` | `#16161A` | — |
| `ink` | `#1B1B1A` | `#F2F2EF` | ≥ 7:1 sur `paper` |
| `ink-quiet` | `#56564F` | `#A3A39C` | ≥ 7:1 sur `paper` |
| `rule` | `#E2E2DB` | `#2E2E34` | aucune (décoratif) |
| `edge` | `#8C8C83` | `#6E6E77` | ≥ 3:1 sur `paper` |

La scission `rule` / `edge` est structurelle : elle empêche d'assombrir toute la page pour rendre conforme une bordure de contrôle.

**Familles.** Deux, toutes deux système. `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` pour tout ce que nous écrivons. `ui-serif, Georgia, "Times New Roman", serif` **exclusivement pour le texte cité**. Le sérif est un marqueur de provenance, jamais un choix esthétique : un seul usage décoratif détruit la convention pour toutes les pages. **Aucune police distante ne sera jamais chargée.**

**Échelle de taille — six valeurs, aucune autre :**
`0.8125rem` (appareil) · `0.9375rem` (secondaire) · `1rem` (base) · `1.125rem` (lecture : énoncés, citations) · `1.375rem` (titre de section) · `1.75rem` (titre de page).

**Graisses : 400 et 600 uniquement.** La graisse **ne change jamais** en fonction d'un état — un contrôle qui passe en gras à la sélection modifie sa largeur et décale la mise en page.

**Interlignage :** 1.6 prose et énoncés · 1.55 citations · 1.25 titres · 1.4 appareil.

**Espacements — cinq valeurs, aucune autre :** 4, 8, 16, 32, 64 px. Contrainte volontairement brutale : une échelle à cinq valeurs se vérifie en revue en quelques secondes.

**Mesure :** 60 à 72 caractères, cap dur à 72. La largeur du conteneur découle de la mesure, jamais l'inverse.

**Focus :** anneau **double achromatique**, 2 px intérieur couleur du fond + 2 px extérieur couleur du texte. Garantit ≥ 3:1 contre n'importe quelle surface, y compris à l'intérieur d'un bloc sélectionné ou sur un bouton à fond `ink`.

**Quatre registres de provenance**, distingués par des moyens cumulés et redondants :

| Registre | Famille | Taille | Marquage |
|---|---|---|---|
| Texte officiel cité | Sérif | lecture | Filet vertical, attribut de langue, référence attenante |
| Notre reformulation (énoncés) | Sans | lecture | Déclaré **une fois** pour tout le questionnaire |
| Notre traduction | Sans | secondaire | Toujours adjacente à l'original, jamais à sa place |
| Notre commentaire (méthode, limites) | Sans | secondaire | Conteneur dédié avec libellé |

**Règle d'économie du marquage :** registre déclaré **une fois par contexte** s'il est uniforme, **par bloc** dès qu'il est mixte (page de résultats). Sans cette règle, l'appareil devient du bruit et cesse d'être lu.

**Animations — liste fermée.** Autorisées : transition de couleur sur survol/appui d'un contrôle (≤ 120 ms) ; ouverture/fermeture native d'un bloc repliable. **Tout le reste est interdit** : apparition, progression, défilement, mise en scène de la révélation, squelette animé, mouvement d'attraction. Toute animation autorisée est supprimée sous préférence de mouvement réduit, et l'interface doit rester **strictement équivalente en information** sans elle.

**Vocabulaire.** Le terme « carte » est proscrit du projet : on dit **enregistrement**, pour éviter l'usage décoratif. Un enregistrement délimite une unité de donnée possédant une identité et une provenance ; il est inerte et jamais cliquable dans son ensemble.

---

## 16. Contraintes d'accessibilité

Ces règles sont des **invariants**, pas un objectif de conformité.

| Règle | Niveau | Conséquence concrète |
|---|---|---|
| Texte à **7:1** | au-dessus de AA | Gratuit sur une interface achromatique : aucune couleur de marque à préserver |
| Bordures d'affordance à **3:1** | WCAG 1.4.11 | Le jeton `edge` existe uniquement pour cela et ne peut jamais être remplacé par `rule` sur un contrôle |
| Anneau de focus à **3:1 contre toute surface adjacente** | WCAG 1.4.11 | Impose l'anneau double : un anneau simple échoue toujours sur au moins un fond |
| **Aucune information par la seule couleur ni la seule valeur de gris** | WCAG 1.4.1 | Le niveau de confiance est un **mot**, jamais une nuance ni une position graphique |
| Cibles **44×44 px** | au-dessus de 2.5.8 (24×24) | Contrainte dimensionnante de tout le produit (voir §18). C'est elle qui, à 320 px, impose le jeu de libellés unique de DP-26 |
| **Focus jamais supprimé**, ordre de focus = ordre du document | WCAG 2.4.3, 2.4.7 | Interdit tout réordonnancement visuel par propriété de mise en page (DT-08) |
| **Contrôles natifs jamais masqués** | — | Condition du mode contraste forcé et de la sémantique sans ARIA |
| **Langue par nœud** | WCAG 3.1.2 | Condition de fonctionnement de la version anglaise : sans elle, la synthèse vocale prononce du français avec des règles anglaises |
| **320 px et zoom 200 %** sans perte | WCAG 1.4.4, 1.4.10 | L'échelle à cinq colonnes est l'élément dimensionnant |
| **Régions vivantes mesurées** | — | Le décompte ne s'annonce pas à chaque sélection : l'annonce native du contrôle confirme déjà l'action |
| **Absence de service signalée** | P8 | Trois états textuellement distincts |

---

## 17. Contraintes de sécurité

**Frontière de confiance côté API.** `valid()` (`api/src/main.rs:52`) vérifie que `choice < 5` et que l'identifiant de question existe. Sans ce contrôle, la table croît sans borne. **Aucune PR ne touche à l'API** ; ce contrôle ne doit pas être contourné côté client par un envoi d'identifiants dérivés d'autre chose que du fichier de questions.

**Échappement.** Le rendu par `innerHTML` et la fonction `escape()` maison de `results.astro` disparaissent en PR-10 au profit de l'échappement natif d'Astro. **Tout endroit contournant le balisage réintroduirait le problème** : après PR-10, aucune occurrence de `innerHTML` ne doit subsister.

**Aucune requête tierce.** Ni police distante, ni analytics, ni CDN, ni script externe. Une police distante serait une requête vers un tiers, contradictoire avec l'absence d'analytics revendiquée.

**Données locales.** Le brouillon (PR-08) vit en `sessionStorage`, **jamais en `localStorage`** : la trace meurt à la fermeture de l'onglet, ce qui est cohérent avec « aucun résultat individuel stocké ». La clé est celle déjà utilisée pour transmettre les réponses à la page de résultats : le delta de vie privée est nul.

**Limite non maîtrisée, à énoncer et non à masquer.** Le serveur de compteurs voit une adresse IP, comme tout serveur. C'est signalé dans un commentaire de `index.astro:99-103` ; P2 impose que ce résidu soit également énoncé dans l'interface (PR-09, PR-13).

**CORS ouvert assumé.** Sans authentification ni données par utilisateur, une restriction d'origine ne protégerait rien.

---

## 18. Contraintes de performance

Le site est **statique**, sans dépendance à l'exécution. Les contraintes sont donc peu nombreuses mais strictes :

- **Aucune requête réseau au chargement** hormis les avoirs du site. Les compteurs sont sollicités **uniquement sur la page de résultats**, après la révélation.
- **Aucune police distante** : pas de décalage de rendu au chargement, pas de point de défaillance.
- **PR-10 augmente le volume HTML** de la page de résultats (rendu statique du détail) en **supprimant** du JavaScript. C'est un arbitrage assumé : 30 questions × jusqu'à 3 positions reste très en deçà de tout seuil problématique.
- **PR-07 impose une permutation avant le premier rendu visible.** Une permutation appliquée après produit un réagencement visible. C'est la seule contrainte de performance à effet perceptible du chantier.
- **PR-12 impose un emplacement réservé de dimension stable** pendant l'attente des compteurs, pour éviter un décalage à l'arrivée des données.

---

## 19. Contraintes de maintenabilité

**Une seule personne maintient ce dépôt.** Toute proposition dont le coût de maintenance dépasse le gain est rejetée par défaut. C'est le motif de DT-01 et DT-02.

**Fewest files possible.** Les composants créés en PR-05 le sont **uniquement** parce que cinq PR identifiées doivent les modifier. Créer un composant utilisé une seule fois et jamais modifié serait une abstraction spéculative.

**Pas de styles par composant.** Le couplage CSS ↔ balisage de `styles.css` est atténué, pas éliminé. Des styles par composant coûteraient plus qu'ils ne rapporteraient sur 600 lignes.

**Les contraintes sont testées, pas documentées.** Une règle qui ne repose que sur la discipline se perd. Les tests de jetons, de contraste et d'aveuglement existent pour que le système survive à une interruption longue et à un contributeur qui n'aurait pas lu cette documentation.

**Une exception connue :** la règle d'économie du marquage des registres (§15) exige un jugement et ne se teste pas. C'est **la seule règle du système reposant entièrement sur la revue humaine**, et elle doit être rappelée dans `REVIEW_CHECKLIST.md`.

---

## 20. Contraintes de réversibilité

**Aucune PR ne modifie de format de données persistant**, hormis la clé de brouillon (PR-08), dont la réversion est sans conséquence puisqu'elle expire à la fermeture de l'onglet.

**Aucune migration de base. Aucun changement d'API. Aucun format de contenu modifié.** La réversibilité est structurellement acquise sur 13 PR sur 14.

**Seule exception : PR-14.** Elle restructure `T` et touche toutes les chaînes et tous les composants de texte. Sa réversion est coûteuse, non par risque de perte de données mais par volume de diff.

**Chaque PR est déployable seule.** Aucune ne laisse le produit dans un état intermédiaire incohérent. Une PR peut être révoquée sans révoquer les suivantes, à l'exception des dépendances listées en §24.

---

## 21. Contraintes de revue

La checklist complète est dans **`REVIEW_CHECKLIST.md`** (37 points). Principes de revue :

- **Une seule réponse défavorable justifie le rejet**, quelle que soit la qualité du reste. Une violation de principe arrête la discussion avant l'examen des mérites.
- **Une PR qui modifie le fichier de jetons relève d'une modification du système d'interface**, pas d'un changement de fonctionnalité, et se traite comme telle.
- **La liste d'exceptions du test de jetons est un signal.** Une liste qui s'allonge de PR en PR est le symptôme mesurable d'un système d'espacement inadapté : c'est le système qu'il faut réviser explicitement, pas contourner.
- **Une règle contournée dans une PR de fonctionnalité est une règle violée**, quelle que soit la justification. Les règles se modifient par une PR dédiée, sans changement d'interface, datée.

---

## 22. Invariants absolus

Liste complète et procédures de vérification : **`INVARIANTS.md`**. Rappel des identifiants :

| Id | Invariant |
|---|---|
| INV-01 | Aveuglement structurel : aucune donnée de formation dans le bundle du questionnaire |
| INV-02 | Aucune statistique agrégée avant la révélation |
| INV-03 | Aucun résultat individuel stocké ; aucune PII, session, IP fine ou horodatage |
| INV-04 | Une requête indépendante par réponse, en ordre aléatoire, sans lien entre elles |
| INV-05 | Refuser la contribution n'envoie **rien du tout** |
| INV-06 | Chaque question porte son document officiel et sa citation exacte, vérifiée mot pour mot en CI |
| INV-07 | Git est la source de vérité ; SQLite ne contient que des entiers |
| INV-08 | Le site est complet sans le service de compteurs |
| INV-09 | Le scoring est intégralement côté client |
| INV-10 | Les contrôles natifs ne sont jamais masqués |
| INV-11 | Le focus n'est jamais supprimé ni atténué |
| INV-12 | Aucune teinte ; aucune information portée par la couleur ou la valeur de gris |
| INV-13 | Aucun nombre sans son dénominateur |
| INV-14 | Une absence de donnée s'affiche comme absence |
| INV-15 | Contenu politique en français ; code, identifiants et commentaires en anglais |
| INV-16 | Aucune dépendance tierce chargée à l'exécution |
| INV-17 | L'ordre de focus est l'ordre visuel |
| INV-18 | L'instrument est identique pour tous, hors tirage d'ordre documenté ; aucun test A/B |

---

## 23. Hors périmètre

Explicitement **hors des 14 PR**, avec le motif :

| Élément | Motif |
|---|---|
| **Page d'accueil / landing** | Abandonnée (DP-07). Elle ne contiendrait que des affirmations sur nous-mêmes, alors que le projet repose sur la preuve. Atterrir directement sur l'instrument est plus honnête. Le besoin réel qu'elle servait est couvert par l'en-tête du questionnaire (**DP-27**, porté par PR-07) et par la page de méthodologie (PR-13) |
| **Wizard une-question-par-écran** | Écarté par principe (DP-08) : il rend l'instrument inauditable pendant son usage |
| **Barre de progression** | Interdite (DP-20, P9) |
| **Métadonnées de partage** (`og:*`) | Reléguées (DP-23). Admissibles pour partager *l'outil*, jamais un résultat, sans slogan ni chiffre d'usage. **Aucune PR ne les traite** |
| **Rééquilibrage du corpus** (couverture, polarité) | Relève de `pipeline/` et `content/`. L'interface peut rendre le déséquilibre honnête, pas le corriger |
| **Date de récolte des documents** | Absente du schéma ; suppose une modification de `pipeline/fetch.py` — voir OQ-03 |
| **Versionnement des items de questionnaire** | Absent du schéma — voir OQ-04 |
| **Modification de l'API** | Aucune n'est nécessaire (DT-10) |
| **Page publique de données agrégées** | Envisagée puis non retenue : DP-15 maintient les agrégats sur la page de résultats |
| **Opt-in ou consentement sans défaut** | Envisagés puis non retenus : DP-04 maintient l'opt-out |
| **Typologies, badges, témoignages, comparaisons sociales, gamification** | Anti-principes du système d'interface |
| **Toute nouvelle dépendance npm** | DT-01 |

---

## 24. Dépendances entre PR

```
PR-01 ─── indépendante de tout

PR-02 ─── (styles.css : sérialisée avec PR-03, voir ci-dessous)
PR-03 ─┘
         └→ PR-04 → PR-05 ─┬→ PR-06 → PR-07 → PR-08 → PR-09
                            └→ PR-10 → PR-11 → PR-12
PR-02 ──────────────────────────────────→ PR-13
PR-11 + PR-12 ─── (section « seuils ») ──→ PR-13
PR-06 + PR-11 ──────────────────────────→ PR-14
```

| PR | Dépend de | Parallélisable avec | Réversion |
|---|---|---|---|
| 01 | — | **02 et 03** | Triviale |
| 02 | — | 01 · **jamais 03** (voir point chaud) | Triviale |
| 03 | — | 01 · **jamais 02** (voir point chaud) | Triviale |
| 04 | 03 | — | Triviale |
| 05 | 04 | — | Triviale (sortie identique) |
| 06, 07, 08, 09 | 05 | PR-10 à PR-13 | Triviale |
| 10 | 05 | 06–09 | Triviale |
| 11, 12 | 10 | 06–09 | Triviale |
| 13 | **02** (dur) · **11 et 12** (section « seuils » uniquement) | 06–12, **sous condition** ci-dessous | Triviale |
| 14 | 06, 11 | **aucune** (DT-16) | Coûteuse |

### Dépendance conditionnelle de PR-13

PR-13 publie les seuils de confiance (PR-11) et de pourcentage (PR-12). DP-11 et DP-15 imposent que
les seuils publiés soient **ceux du code, lus et jamais recopiés**. Deux cas, tous deux admis :

- **PR-11 et PR-12 fusionnées** → PR-13 publie la section « mode de calcul et seuils » et son critère
  « seuils affichés = seuils du code » s'applique.
- **PR-11 ou PR-12 non fusionnée** → PR-13 est menée **sans** cette section, et la description de la
  PR déclare explicitement que la section est différée. Le critère correspondant est alors sans objet.

**Interdit dans les deux cas :** recopier une valeur de seuil dans la page de méthodologie.

**Points chauds Git :**
- **`web/src/styles.css` — le point de conflit unique du chantier.** Touché par PR-02, 03, 06, 09,
  11, 12, 13, 14. DT-15 impose que **PR-03 seule le restructure** ; toutes les autres n'y ajoutent
  que des blocs en fin de fichier. **Conséquence directe : PR-02 et PR-03 ne peuvent pas être
  ouvertes simultanément**, PR-03 réécrivant l'intégralité du fichier auquel PR-02 ajoute. L'ordre
  entre elles est libre ; leur simultanéité ne l'est pas.
- `web/src/lib/ui.js` — touché par huit PR, mais par **ajouts de clés**, dont les conflits se
  résolvent mécaniquement. **PR-14 le restructure** et entrera en conflit avec toute PR en vol (DT-16).

---

## 25. Stratégie de migration incrémentale

**Cinq règles de découpage :**

1. **Le garde-fou avant le chantier.** L'invariant d'aveuglement n'est protégé par aucun test aujourd'hui. Refactoriser un questionnaire aveugle sans test d'aveuglement est la seule erreur véritablement irrattrapable.
2. **Sérialiser `styles.css`.** Une seule PR le restructure (PR-03) ; les suivantes n'y **ajoutent** que des blocs.
3. **Extraire les composants tôt.** Cinq PR doivent modifier le questionnaire. Sans extraction préalable, elles se disputent le même fichier de 117 lignes.
4. **Séparer migration de rendu et changement de sémantique.** La page de résultats subit deux transformations de nature différente (PR-10 puis PR-11) ; les fusionner rendrait la revue impossible et la régression indétectable.
5. **Chaque PR est déployable seule.**

**Séquence complète :** voir `ROADMAP.md`.

---

## 26. Pourquoi ce découpage

Trois questions reviennent et méritent une réponse explicite pour éviter qu'une session future ne « simplifie » la séquence.

**Pourquoi PR-01 en premier, alors qu'elle ne change rien pour l'utilisateur ?**
Parce que l'invariant d'aveuglement est le seul dont la violation soit irrattrapable : une révélation prématurée ne se corrige pas, elle s'est produite. Les PR-05 à PR-14 déplacent du balisage et des imports entre fichiers ; sans contrôle automatisé, un import de programme ajouté par inadvertance dans le questionnaire ne serait détecté par personne.

**Pourquoi PR-05 (extraction de composants) plutôt que modifier directement les pages ?**
Parce que cinq PR identifiées — 06, 07, 08, 09, 14 — doivent modifier le questionnaire. Sans extraction, elles se disputent le même fichier. L'extraction n'est pas une abstraction spéculative : elle est justifiée par des modifications **déjà planifiées et nommées**. Sa neutralité est vérifiable par comparaison octet à octet de la sortie compilée (DT-20), ce qui en fait la PR la plus sûre du chantier.

**Pourquoi séparer PR-10 (rendu) et PR-11 (sémantique) ?**
PR-10 change *comment* le contenu est produit sans changer *ce qui* est affiché : elle est intégralement revuable par comparaison. PR-11 change ce qui est affiché sans changer comment : elle est revuable par lecture. Fusionnées, aucune des deux méthodes ne s'applique et toute régression devient indétectable.

---

## 27. Stratégie de validation

**Trois niveaux, cumulatifs.**

**Niveau 1 — automatisé, bloquant en CI.**
`pipeline.check` (contenu, citations mot pour mot) · `npm test` (score, jetons, contraste) · contrôle d'aveuglement sur la sortie compilée (PR-01) · `cargo test` (compteurs).

**Niveau 2 — comparaison de sortie.** Trois protocoles distincts, selon ce que la PR change (DT-20) :

| PR | Ce qui change | Protocole |
|---|---|---|
| **PR-03** | Le style, **aucun balisage** | HTML compilé **identique octet à octet** sur les quatre pages ; seul le CSS émis diffère |
| **PR-05** | L'emplacement du balisage | HTML compilé **identique octet à octet, différence nulle** |
| **PR-10** | Le **mode de production** du HTML | Les octets changent nécessairement. Comparaison du **texte rendu extrait du DOM final** (questions masquées exclues) et des **ordres**, sur trois jeux de réponses |
| **PR-06** | La grille de réponse | Relevé aux **neuf largeurs** : 320, 360, 375, 414, 480, 600, 768, 1024, 1600 px |
| **PR-07** | L'ordre d'affichage | Cinq rechargements pour l'ordre de tabulation ; **protocole de première peinture** avec limitation réseau, trois fois |

**Aucune différence n'est justifiable.** Si une différence apparaît, la PR est bloquée et la cause corrigée.

**Niveau 3 — vérification manuelle normée (M1–M8).**
Aucun test de navigateur automatisé n'est introduit (DT-02). La vérification manuelle est donc **normée et référencée par identifiant** dans chaque PR.

| Id | Vérification |
|---|---|
| **M1** | Parcours clavier complet : tabulation, focus toujours visible, aucun piège, **ordre de focus identique à l'ordre visuel** |
| **M2** | Lecteur d'écran : annonce des groupes, des positions, des états ; verbosité acceptable sur 30 items |
| **M3** | **320 px** de largeur : aucun défilement horizontal, échelle non repliée, cibles ≥ 44 px |
| **M4** | **Zoom 200 %** : aucune perte de contenu ni de fonction |
| **M5** | **Mode contraste forcé** du système : contrôles visibles et distinguables |
| **M6** | **Thème clair et thème sombre** |
| **M7** | **JavaScript désactivé** : comportement conforme à ce qui est annoncé |
| **M8** | **Sans service de compteurs** (`PUBLIC_CIVIS_API` vide) **et** avec service injoignable |

---

## 28. Stratégie de tests

**Tests existants à préserver :**
- `web/src/lib/score.test.mjs` — 7 tests couvrant : accord total = 1, désaccord total = 0, inversion du classement, réponses à demi-intensité, point médian, exclusion des réponses neutres et sautées, restriction d'une formation à ses propres questions, aller-retour de l'échelle par `choiceIndex`.
- `api/src/main.rs` — 4 tests : accumulation par question et choix, échelle complète pour une question sans réponse, rejet des questions inconnues et des choix hors échelle, non-corruption de la réponse par une ligne hors échelle en base.

**Tests créés par la migration :**

**Tests obligatoires créés par la migration :**

| Test | PR | Ce qu'il garantit |
|---|---|---|
| **Aveuglement** | PR-01 | Aucun identifiant, nom ou sigle de formation dans la page de questionnaire compilée ni dans les avoirs JS qu'elle référence |
| **Contraste** | PR-03 | Ratios calculés depuis les valeurs de jetons, échec sous les seuils |
| **Jetons** | PR-03 | Aucune valeur hexadécimale hors du fichier de jetons ; aucune longueur ou taille hors échelle ; aucune durée hors borne ; **aucun attribut `style=` inline** ; aucune propriété de teinte |
| **Score étendu** | PR-11 | Fraction, couverture, un test par palier de confiance **aux bornes**, formation à couverture nulle |

**Tests recommandés, à écrire si la logique concernée est extraite en fonction pure** — chacun couvre
une logique non triviale sur un chemin où une erreur est silencieuse (règle K8 de la checklist) :

| Test | PR | Ce qu'il garantit |
|---|---|---|
| Permutation | PR-07 | Le mélange produit une permutation valide : même longueur, mêmes éléments, aucun perdu ni dupliqué |
| Aller-retour du brouillon | PR-08 | Sérialisation → restauration conserve réponses **et** ordre. Chemin de perte de données |
| Seuil d'effectif | PR-12 | Effectif nul, juste sous le seuil, juste au-dessus |
| Couverture du corpus | PR-13 | Retrouve `nfp` 19, `rn` 15, `ensemble` 10, `lr` 4 et 14 questions mono-formation. Échouera utilement le jour où le corpus changera |
| Parité des clés de `T` | PR-14 | Toute clé de `T.fr` existe dans `T.en` et réciproquement. Régression la plus probable de PR-14 |

**Ce qui n'est pas testé et reste manuel :** tout ce qui relève du rendu, du clavier, du lecteur d'écran, du contraste forcé et des largeurs. C'est le prix assumé de DT-02.

---

## 29. Stratégie de rollback

**Par PR.** Chaque PR est une révocation Git simple. Aucune donnée n'est migrée, aucun format persistant n'est modifié (§20).

**Cas particuliers :**

| PR | Précaution au rollback |
|---|---|
| PR-08 | Un brouillon écrit par la version révoquée peut subsister dans l'onglet ouvert d'un utilisateur. Sans conséquence : la clé est celle déjà utilisée, le format doit rester compatible avec la lecture qu'en fait la page de résultats |
| PR-11 | La révocation restaure le pourcentage. Vérifier que `score.test.mjs` a bien été restauré dans sa version correspondante |
| PR-13 | La page de méthodologie disparaît : vérifier qu'aucun lien orphelin ne subsiste dans `Base.astro` ou dans les composants |
| PR-14 | Révocation coûteuse par volume. À traiter comme une PR à part entière |

**Rollback de production.** Le site étant statique et publié à chaque poussée sur `main`, une révocation suivie d'une poussée republie l'état antérieur en un cycle de CI complet — incluant `pipeline.check`, qui nécessite le réseau pour la vérification des citations.

---

## 30. Glossaire

| Terme | Définition dans ce projet |
|---|---|
| **Aveuglement** | Propriété selon laquelle aucune affiliation politique n'atteint le navigateur avant la dernière réponse. **Structurelle**, pas déclarative : le fichier de questions ne contient aucune donnée de formation |
| **Révélation** | Moment où l'affiliation est affichée, c'est-à-dire la page de résultats. **Conséquence de la méthode, jamais un événement à mettre en scène** |
| **Formation** | Une organisation politique du corpus. Terme du lexique fixe ; ne pas écrire « parti » dans l'interface |
| **Proposition** | Un point de programme cité, issu d'un document officiel |
| **Reformulation** | Un énoncé de questionnaire, **écrit par nous** à partir d'une proposition. N'est pas une citation |
| **Citation** | Extrait **mot pour mot** d'un document officiel, vérifié en CI |
| **Document source** | Le document officiel dont dérive une proposition, avec titre, date de publication, URL et empreinte |
| **Empreinte** | SHA-256 d'un document source, commité dans `content/sources/<élection>/<id>.sha256` au format `<empreinte>  <url>` |
| **Couverture** | Nombre de propositions du questionnaire sur lesquelles une formation possède une position identifiée. **Propriété du jeu de données**, indépendante des réponses de l'utilisateur |
| **Base de comparaison** | Nombre de propositions effectivement comparées pour un utilisateur donné : questions auxquelles il a répondu de façon non neutre **et** sur lesquelles la formation se positionne |
| **Niveau de confiance** | Qualification textuelle du résultat, issue d'une règle publiée et déterministe fondée sur la base de comparaison. **Plafonné** : le corpus actuel ne peut soutenir aucune qualification supérieure à « partielle » |
| **Appareil** | Ensemble des mentions qui qualifient un contenu : provenance, date, registre, base, effectif, limites. Niveau 2 de la hiérarchie. **Jamais supprimable pour alléger une page** |
| **Appareil de version** | Pied de page portant commit de construction, date, liens vers le dépôt et la vérification. Le « numéro de série » de l'instrument |
| **Registre** | Statut d'un bloc de texte : officiel cité, notre reformulation, notre traduction, notre commentaire |
| **Enregistrement** | Bloc délimité correspondant à une unité de donnée avec identité et provenance. Remplace le terme « carte », proscrit |
| **Portée** | Composant énonçant ce qu'un contenu **ne montre pas**. Ni message d'erreur, ni alerte. Jamais fermable |
| **Effectif** | Nombre de **réponses enregistrées pour une proposition**. Jamais un nombre de personnes, structurellement inconnaissable |
| **Opt-out** | Contribution aux compteurs activée par défaut, désactivable. Refuser n'envoie rien du tout |
| **Brouillon** | Réponses en cours conservées en `sessionStorage` avec l'ordre tiré. Meurt à la fermeture de l'onglet |
| **M1–M8** | Vérifications manuelles normées (§27) |
| **P1–P10** | Les dix principes normatifs (§12) |
| **DP / DT / INV / OQ** | Décision produit / décision technique / invariant / question ouverte |

---

## 31. Manques documentés hors périmètre `web/`

**Aucune question ouverte ne subsiste.** Toutes les décisions nécessaires à l'implémentation des
quatorze PR sont arrêtées et consignées dans `DECISIONS.md`. Les deux points ci-dessous ne sont
**pas** des décisions à prendre : ce sont des **manques du schéma de contenu**, dont la correction
relève de `content/` et `pipeline/`, hors du périmètre de ce chantier. Ils ne bloquent aucune PR.

Une seule vérification factuelle reste à effectuer avant d'écrire PR-01 : **OQ-08**, ci-dessous.

### OQ-03 — Date de récolte des documents sources

**Manque.** P6 exige une date de récolte. `content/sources/fr-2027/sources.json` ne porte que `published`. Aucun fichier du dépôt ne contient de date de récolte.
**Pourquoi c'est problématique.** Satisfaire pleinement P6 exige que `pipeline/fetch.py` enregistre cette date, que le schéma de `sources.json` évolue et qu'un contrôle soit ajouté dans `pipeline.check` — soit une PR **hors du périmètre `web/`**.
**PR impactées.** PR-13, qui doit livrer ce qui est disponible (titre, date de publication, empreinte, URL) sans la date de récolte.
**Statut :** l'appareil documentaire restera incomplet au regard du système tant que cette PR pipeline n'est pas livrée. **Non bloquant pour PR-13.**

### OQ-04 — Versionnement des items de questionnaire

**Manque.** `content/questions/fr-2027.json` n'a ni champ de version ni date par item. Une reformulation ne laisse d'autre trace que l'historique git.
**Pourquoi c'est problématique.** INV-18 (instrument identique pour tous, aucun test A/B) et la traçabilité de l'instrument supposent que chaque question soit versionnée. À défaut, des compteurs porteront sur des formulations différentes sous un même identifiant.
**PR impactées.** Aucune des 14 n'est bloquée. Impacte la validité des agrégats sur une période longue.
**Porteur du rappel : PR-13.** C'est la seule PR qui documente la traçabilité de l'instrument ; elle doit **signaler ce manque dans sa description**, faute de quoi OQ-04 n'a aucun point de remontée et sera oubliée. PR-13 ne le corrige pas : la correction est côté `content/` et `pipeline/`.
**Statut :** acceptable à court terme ; à traiter côté contenu avant toute publication d'agrégats sur longue durée.

### OQ-08 — Présence d'un nom de formation dans un énoncé de question

**Vérification non faite.** PR-01 construit sa liste d'interdits depuis `content/programs/`. Si un nom ou un sigle de formation apparaît légitimement dans un énoncé de question, le contrôle échouera.
**Pourquoi c'est problématique.** C'est une décision de contenu, pas un paramétrage de test : un énoncé nommant une formation violerait INV-01.
**PR impactées.** PR-01.
**Statut :** **à vérifier avant d'écrire PR-01.** Si un tel cas existe, il doit être traité comme un défaut de contenu.
