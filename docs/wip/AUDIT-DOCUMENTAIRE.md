# Civis — Audit documentaire

**Statut : temporaire.** Ce document est un document de travail. Il est supprimé
par la PR qui livre la réorganisation qu'il propose. Il est lui-même le premier
cas d'application de la politique de cycle de vie du §5.

**Périmètre.** Les 8 fichiers Markdown du dépôt, 4 039 lignes. Aucun code n'a
été modifié. Aucun document n'a été supprimé.

**Méthode.** Lecture intégrale des 8 fichiers, puis vérification de leurs
affirmations contre l'état réel du dépôt : références de fichiers, références de
lignes, métriques du corpus recalculées, présence des composants, contenu des
workflows CI.

---

## Sommaire

0. [Constat bloquant : la documentation n'est pas versionnée](#0--constat-bloquant--la-documentation-nest-pas-versionnée)
1. [Inventaire et verdict par fichier](#1--inventaire-et-verdict-par-fichier)
2. [Constats d'audit](#2--constats-daudit)
3. [Proposition, document par document](#3--proposition-document-par-document)
4. [Architecture documentaire cible](#4--architecture-documentaire-cible)
5. [Politique de cycle de vie](#5--politique-de-cycle-de-vie)
6. [Plan de contenu des documents à créer](#6--plan-de-contenu-des-documents-à-créer)
7. [Table de sauvetage avant suppression](#7--table-de-sauvetage-avant-suppression)
8. [Conséquences sur la DP Impacts](#8--conséquences-sur-la-dp-impacts)
9. [Risques](#9--risques)
10. [Questions restantes](#10--questions-restantes)

---

## 0 — Constat bloquant : la documentation n'est pas versionnée

`.gitignore:1-3` — ajouté et non commité, visible dans `git diff` :

```
# Temporary docs
*.md
```

**Conséquence.** `docs/` n'est **pas** suivi par git. `git ls-files` renvoie 57
fichiers, aucun sous `docs/`. Les quatre documents de `docs/migration/`, la DP
Impacts et le présent audit n'existent **que sur cette machine**.

`README.md` et `content/README.md` échappent à la règle parce qu'ils étaient
déjà suivis quand elle a été ajoutée — git continue de suivre un fichier déjà
suivi. Ce n'est pas une exception voulue, c'est un effet de bord.

**`CLAUDE.md` n'a jamais été commité** — `git log -- CLAUDE.md` est vide. Le seul
document que lit systématiquement une session d'assistance, celui qui porte les
invariants du projet, n'existe pas dans le dépôt.

**Pourquoi c'est bloquant.** `DECISIONS.md:4` énonce : *« aucune décision de ce
registre ne se réinterprète »*. Un registre normatif absent du dépôt n'est
opposable à personne, ne survit pas à une panne de disque, et n'a pas
d'historique — or c'est précisément l'historique diffable qui est l'argument du
projet (DP-06).

**Plus grave encore pour la suite de ce travail :** supprimer un fichier de
`docs/migration/` aujourd'hui est une **perte définitive**, pas une suppression
git récupérable.

> **Prérequis absolu à toute suppression :** corriger `.gitignore` et commiter
> l'état actuel de `docs/` **avant** la PR de réorganisation. Sinon la
> réorganisation détruit 2 415 lignes sans trace.

**Correction — faite.** La règle `*.md` a été retirée. `docs/` est de nouveau
suivi-able ; `review/`, `.cache/`, `web/dist/` et les autres exclusions sont
intactes. Aucune règle `docs/scratch/` n'a été ajoutée, et il n'en faut pas :
les brouillons de session vivent hors du dépôt. La mention de `docs/scratch/`
est retirée de l'arborescence cible du §4.

**Reste à faire, dans cet ordre :**

1. Répondre à **Q-8** (publication) — c'est le commit qui rend `docs/` public,
   donc le point de non-retour.
2. Commiter `docs/` **et `CLAUDE.md`** dans leur état actuel, sans rien modifier.
3. Seulement ensuite, la PR de réorganisation.

---

## 1 — Inventaire et verdict par fichier

| Fichier | Lignes | Rôle | État factuel | Verdict |
|---|---|---|---|---|
| `README.md` | 156 | Entrée publique | Exact sauf 3 points | **Modifier** |
| `CLAUDE.md` | 62 | Instructions d'agent | Exact | **Modifier** (ajouts) |
| `content/README.md` | 73 | Schéma de contenu | Exact | **Modifier** (ajouts) |
| `docs/migration/MIGRATION.md` | 875 | Cadre du chantier d'interface | **Chantier terminé.** §6, §10, §11, §24–§29 décrivent un état qui n'existe plus | **Éclater puis supprimer** |
| `docs/migration/DECISIONS.md` | 1 016 | Registre DP-01→28 / DT-01→20 | Décisions **toujours valides**. Champs « Impact PR » devenus historiques | **Déplacer + toiletter** |
| `docs/migration/INVARIANTS.md` | 304 | INV-01→18 | Invariants valides ; **rédaction au futur**, protections décrites comme à venir | **Déplacer + réécrire au présent** |
| `docs/migration/REVIEW_CHECKLIST.md` | 220 | Checklist de revue, 37 points | Contenu majoritairement valide, **inopposable en l'état** (A1 rejette toute PR) | **Réécrire + renommer** |
| `docs/impacts/DECISION.md` | 1 333 | DP Impacts | Exacte, non implémentée | **Déplacer + renommer** |

---

## 2 — Constats d'audit

### 2.1 Le chantier documenté est terminé — la documentation ne le sait pas

Vérifié dans le dépôt : les quatorze PR décrites par `MIGRATION.md` ont toutes
été livrées.

| Livrable annoncé | PR | Présent aujourd'hui |
|---|---|---|
| Contrôle d'aveuglement sur la sortie compilée | PR-01 | `web/scripts/check-blindness.mjs`, exécuté par `pages.yml` |
| Appareil de version (commit, date, build local) | PR-02 | `Base.astro:38-49`, `paths.js` |
| Fichier de jetons, tests de jetons et de contraste | PR-03 | `tokens.css`, `tokens.test.mjs`, `contrast.test.mjs` |
| Suppression de la pré-sélection | PR-04 | Aucune pré-sélection dans `Question.astro` / `AnswerScale.astro` |
| Composants du questionnaire | PR-05 | `Question.astro`, `AnswerScale.astro` |
| Grille de réponse, jeu de libellés unique | PR-06 | `CHOICE_LABELS_SHORT` dans `ui.js` |
| Tirage d'ordre, en-tête à cinq énoncés | PR-07 | `index.astro:142-199`, `t.header(...)` |
| Brouillon et bandeau de restauration | PR-08 | `lib/draft.js`, `DraftNotice.astro` |
| Bloc de fin, exposition littérale du payload | PR-09 | `ClosingBlock.astro` |
| Rendu statique des résultats | PR-10 | `results.astro` rendu au build ; **plus aucun `innerHTML`, plus aucun `escape()`, plus aucun `style=`** |
| Fraction, confiance, couverture, provenance | PR-11 | `score.js` (`confidence`, `coverage`, `CONFIDENCE_LEVELS`), `Result.astro`, bloc `provenance` |
| Trois états d'absence des compteurs | PR-12 | `Statistic.astro`, `results.astro:302-338` |
| Page de méthodologie | PR-13 | `pages/[lang]/method.astro` |
| Anglais aide à la lecture | PR-14 | `reading()`, `ui.test.mjs` (parité des clés) |

**Conséquence.** Les sections suivantes de `MIGRATION.md` décrivent un passé au
présent, ce qui en fait des affirmations fausses :

| Section | Affirmation | Réalité |
|---|---|---|
| §6 | « Le front tient en **9 fichiers versionnés**, environ 600 lignes » | 20 fichiers sous `web/src` |
| §6 | « **Il n'existe aucun répertoire `components/`** » | 8 composants |
| §6 | `results.astro` 189 lignes, `index.astro` 117, `ui.js` 86 | 339, 325, 440 |
| §6 | Contrastes : `--line` à 1,37:1, « échec net » | Jetons remplacés, test de contraste en CI |
| §10 | Duplications D1–D6, `escape()`, `innerHTML`, 8 `style=` inline | **Toutes résolues** — vérifié par `grep`, zéro occurrence |
| §11 | 13 défauts « constatés », dont l'option « Passer » pré-cochée | Tous corrigés |
| §24–§26 | Dépendances entre PR, points chauds Git, ordre | Sans objet |
| §27–§29 | Protocoles de comparaison, rollback par PR | Sans objet en tant que plan ; **M1–M8 reste utile** |

**Ce qui reste vrai dans `MIGRATION.md` :** §3 (contexte), §4 (architecture),
**§8 (métriques du corpus — recalculées ce jour, exactes au chiffre près)**,
§9 (API), §12 (P1–P10), §15–§21 (contraintes), §30 (glossaire), §31 (manques).

### 2.2 Métriques du corpus : recalculées, toujours exactes

Contrairement au reste de `MIGRATION.md` §6–§11, le §8 tient. Recalcul de ce
jour sur `content/` :

| Affirmation `MIGRATION.md` §8 | Recalcul | Verdict |
|---|---|---|
| 30 questions | 30 | ✔ |
| Thèmes `economy ×5, social ×5, ecology ×5, institutions ×3, security ×4, health ×3, immigration ×3, europe ×2` | identique | ✔ |
| `education` présent dans `THEMES`, utilisé par aucune question | confirmé | ✔ |
| Couverture `nfp` 19, `rn` 15, `ensemble` 10, `lr` 4 | identique | ✔ |
| Positions par question : 1×14, 2×14, 3×2, jamais 4 | identique | ✔ |
| Polarité `nfp` 15/4, `rn` 13/2, `ensemble` 6/4, `lr` 2/2 | identique | ✔ |
| Énoncé français : moyenne 89, maximum 120 caractères | 89 / 120 | ✔ |

**C'est important.** DP-11 (bornes de confiance 4 et 10), DP-26 (libellés
dimensionnés) et DP-27 (cap à 120 caractères) sont **dérivés de ces mesures**.
Elles restent valides, donc ces décisions restent justifiées. Le §8 doit être
sauvé intégralement, pas résumé.

**Chiffre non documenté et utile :** `content/programs/` compte **72 points**,
dont **48 seulement sont référencés** par `positions.json`. Les 24 autres
n'apparaissent nulle part dans le produit. Cela concerne directement DT-24 de la
DP Impacts, qui limite la génération aux points référencés.

### 2.3 Références cassées

| Référence | Emplacements | État |
|---|---|---|
| `docs/migration/PR-XX.md` | `MIGRATION.md:7`, `REVIEW_CHECKLIST.md:14`, `:211` | **Ces 14 fichiers n'existent pas** |
| `ROADMAP.md` | `MIGRATION.md:714` | **N'existe pas** |
| « la feuille de route » | `REVIEW_CHECKLIST.md:18`, `:166` | **N'existe pas** |
| **« Système §x.y » — le système d'interface** | `REVIEW_CHECKLIST.md`, **17 occurrences** (§1.3, §3.1, §3.2, §3.3, §3.5, §3.7, §5.2, §5.3, §7.3, §7.8, §8.1×2, §8.2×3, §8.3, §8.4) + 5 renvois en prose dans `MIGRATION.md` | **Ce document n'a jamais existé dans le dépôt** |

Le dernier est le plus grave : **17 règles de revue sont opposables contre un
document que personne ne peut lire.** `MIGRATION.md:475` le reconnaît à demi-mot
— *« Référence complète : le système d'interface. Extrait opérationnel »* — mais
l'extrait ne porte pas de numéros de section, donc les renvois ne résolvent pas.

**Conséquence pratique :** `REVIEW_CHECKLIST.md` A1 (« La PR correspond-elle à
un fichier `PR-XX.md` existant ? → rejet si non ») **rejette mécaniquement
toute PR future**. La checklist est aujourd'hui inutilisable telle quelle.

### 2.4 Références de lignes de code : périmées côté `web/`, valides côté `api/`

Échantillon vérifié :

| Référence | Ce qu'elle devait désigner | Ligne réelle aujourd'hui |
|---|---|---|
| `score.js:39` | `CHOICES = [-1,-0.5,0,0.5,1]` | `if (Math.sign(answer) === stance)` — `CHOICES` est en `:142` |
| `paths.js:18` | `API` | `export const API = …` — **par coïncidence, toujours juste** |
| `ui.js:39` | `T.progress()` | ligne vide |
| `styles.css:128` | `:has(input:checked)` | `.choices label {` |
| `index.astro:41` | l'option « Passer » pré-cochée | un commentaire sur DP-27 |
| `results.astro:162` | retrait silencieux de la section | `}` |
| `api/src/main.rs:52` | `valid()` | **`fn valid(...)` — exact** |
| `api/src/main.rs:18` | commentaire de largeur d'échelle | **exact** |

**Règle qui se dégage :** toutes les références vers `web/` ont dérivé ; celles
vers `api/` tiennent, **parce que DT-10 interdisait d'y toucher**. C'est une
démonstration involontaire du coût d'une référence par numéro de ligne.

**Décision proposée :** la documentation permanente ne cite **jamais** un numéro
de ligne. Elle cite un fichier et un symbole (`score.js › CONFIDENCE_LEVELS`),
qui survit à une insertion. Les numéros de ligne restent admis dans un document
temporaire, qui meurt avant d'avoir le temps de dériver.

### 2.5 Décisions qui ne sont plus vraies

| Où | Affirmation | État réel |
|---|---|---|
| `INVARIANTS.md:236` | INV-14 — « **Ce qui le protège. Rien aujourd'hui** : `results.astro:162-163` retire silencieusement la section. Écart connu, corrigé par PR-12 » | **Corrigé.** `Statistic.astro` rend les trois états ; l'invariant est protégé |
| `INVARIANTS.md:280` | INV-17 — « **PR-07 met cet invariant en danger** » | PR-07 est livrée ; le danger est passé, le mécanisme (déplacement DOM) est en place |
| `INVARIANTS.md:192, 206` | INV-11, INV-12 — « **À partir de PR-03** » | Livré |
| `INVARIANTS.md:44` | INV-01 — « **À partir de PR-01** : un contrôle exécuté après `npm run build` » | Livré |
| `MIGRATION.md:236` | « `check.py` … contient un ensemble `THEMES` en dur qui duplique `ui.js` **sans lien mécanique** » | **Toujours vrai.** Duplication D5 non résolue. À conserver comme dette connue |
| `MIGRATION.md:874` | OQ-08 — « à vérifier avant d'écrire PR-01 » | **Résolu** : le contrôle passe en CI, donc aucun nom de formation ne figure dans un énoncé |
| `MIGRATION.md:855` | OQ-03 — date de récolte absente | **Toujours ouvert** : `sources.json` ne porte que `published` |
| `MIGRATION.md:862` | OQ-04 — versionnement des items | **Toujours ouvert** : aucun champ de version dans `questions/fr-2027.json` |
| `README.md:61` | « Pipeline : Python + **API Claude (batch)** » | Vrai aujourd'hui, **destiné à devenir faux** (§8) |
| `README.md:125` | `export ANTHROPIC_API_KEY=…` | Idem |

### 2.6 Doublons

| Doublon | Emplacements | Gravité | Traitement |
|---|---|---|---|
| Registre DP/DT | `MIGRATION.md` §13 et §14 (résumé) **et** `DECISIONS.md` (complet) | **Élevée** — les bornes de DP-11 et le seuil de DP-15 sont écrits deux fois | Supprimer le résumé ; le registre est la seule source |
| Liste des invariants | `MIGRATION.md` §22 **et** `INVARIANTS.md` | Moyenne | Supprimer le rappel ; garder un lien |
| Architecture (4 domaines) | `README.md` §Architecture **et** `MIGRATION.md` §4 **et** `CLAUDE.md` §Structure | Faible — trois publics différents, trois niveaux de détail | Conserver les trois, mais **une seule est normative** (`ARCHITECTURE.md`) ; les deux autres sont des résumés d'accueil |
| Schéma de contenu | `content/README.md` **et** `MIGRATION.md` §8 | Faible | `content/README.md` fait foi ; §8 garde les **métriques**, pas le schéma |
| Garanties CI | `README.md`, `content/README.md`, `INVARIANTS.md`, `MIGRATION.md` §27 | Moyenne | Énoncer la liste **une fois** dans `content/README.md` ; les autres y renvoient |

### 2.7 Ce qui manque entièrement

Aucun document ne couvre aujourd'hui :

1. **La doctrine IA** — pourquoi un LLM, ce qu'on lui confie, ce qu'on ne lui
   confie jamais, d'où vient la neutralité. DP-17 fixe quatre faits à publier
   dans l'interface ; rien ne documente le raisonnement.
2. **La philosophie du produit** — la hiérarchie document → citation →
   reformulation → explication, et l'interdiction pour un niveau de remplacer
   celui du dessus.
3. **La gouvernance** — quand une DP est requise, comment une décision se
   remplace, comment la neutralité est préservée dans le temps.
4. **Le système d'interface** — cité 17 fois, jamais écrit.
5. **Une politique de cycle de vie documentaire** — d'où vient toute la
   situation constatée ici.

---

## 3 — Proposition, document par document

### 3.1 `README.md` — **conserver, modifier**

**Ce qui change.**

1. §Architecture, ligne 61 : remplacer « **API Claude (batch)** » par « **API de
   modèle de langage (traitement par lots, hors ligne)** ». Motif : le tableau
   décrit une architecture, pas un fournisseur ; DT-29 pose que le fournisseur
   est un détail d'implémentation.
2. §Génération des questions, ligne 125 : remplacer `ANTHROPIC_API_KEY` par une
   formulation neutre renvoyant à `docs/AI.md` pour la variable en vigueur.
   **Une clé d'API nommée dans le README est la seule ligne du fichier qui
   devient fausse à chaque changement de fournisseur.**
3. Ajouter une section **« Où lire quoi »** de six lignes, table d'entrée de
   `docs/`. C'est ce qui manque le plus aujourd'hui : rien, dans le dépôt
   publié, n'indique qu'une documentation existe.
4. Ajouter un renvoi vers `docs/AI.md` depuis §Vérifiabilité.

**Ce qui ne change pas.** Le reste est exact, y compris §Vie privée,
§Déploiement et §Accessibilité, vérifiés contre `pages.yml` et le code.

### 3.2 `CLAUDE.md` — **conserver, modifier**

**Ce qui change.** Trois ajouts courts, sans allonger le fichier de plus de
dix lignes :

1. Sous §Invariants : *« Une explication générée n'est jamais substituée à une
   citation. »* — l'invariant produit de la fonctionnalité Impacts, énoncé là où
   une session le lit en premier.
2. Sous §Structure : la ligne `docs/` et sa fonction.
3. Sous §Non-objectifs : reprendre en une ligne les quatre interdits durables de
   la DP Impacts (notation, chiffrage, fact-checking, personnalisation).

**Motif.** `CLAUDE.md` est le seul document que lit systématiquement une session
d'assistance. Un invariant absent de ce fichier est un invariant qu'une session
peut casser de bonne foi.

### 3.3 `content/README.md` — **conserver, modifier**

**Ce qui change.**

1. Quatrième famille de fichiers : `impacts/<élection>.json` (après approbation
   de la DP).
2. §« Ce que la CI garantit » devient **la liste unique et faisant foi** des
   garanties de `pipeline.check`. Les autres documents y renvoient au lieu de la
   recopier — c'est le doublon 2.6 traité à sa racine.

### 3.4 `docs/migration/MIGRATION.md` — **éclater, puis supprimer**

**Justification de la suppression.** 875 lignes dont environ 340 décrivent un
état du dépôt qui n'existe plus, et environ 180 décrivent une planification
achevée. Conserver le fichier en l'annotant « historique » n'est pas une option :
un lecteur qui ouvre §6 lit une description factuellement fausse du front-end.
Le rôle du document — cadrer un chantier — a disparu avec le chantier.

**Ce qui est sauvé avant suppression :** voir la table de sauvetage du §7.
Environ 250 lignes sur 875 migrent vers quatre documents permanents.

### 3.5 `docs/migration/DECISIONS.md` — **déplacer, toiletter, ne jamais réécrire**

**Nouveau chemin :** `docs/decisions/REGISTRY.md`.

**Justification du maintien intégral.** Les 48 décisions restent vraies. Leur
valeur est en grande partie dans les **alternatives rejetées** : sans elles, une
session future reproposera l'opt-in, le pourcentage, la barre de progression, le
wizard ou la palette de couleur, et il faudra refaire le raisonnement.

**Toilettage — strictement limité.**

1. Le champ **« Impact PR »** devient **« Impact »** et cite un fichier ou un
   symbole. Les numéros de PR d'un chantier terminé ne désignent plus rien.
2. Corriger les rares renvois vers `MIGRATION.md §x` en renvois vers le nouveau
   document d'accueil.
3. **Aucune décision n'est réécrite, reformulée, fusionnée ni supprimée.** Un
   registre qu'on toilette au fond est un registre auquel on ne peut plus se
   fier.

**Règle d'immuabilité à inscrire en tête :** une décision se **remplace** par une
nouvelle décision portant un nouvel identifiant, avec les champs
`Remplace :` / `Remplacée par :`. Elle ne se modifie pas sur place.

### 3.6 `docs/migration/INVARIANTS.md` — **déplacer, réécrire au présent**

**Nouveau chemin :** `docs/INVARIANTS.md`.

**Ce qui change.** Le document est écrit du point de vue d'avant le chantier :
« à partir de PR-01 », « PR-07 met cet invariant en danger », « rien ne le
protège aujourd'hui ». Ces formules étaient exactes ; elles ne le sont plus.

Chaque entrée est réécrite au **présent**, avec la même structure — *Énoncé /
Pourquoi il existe / Ce qui le protège / Comment il peut être cassé / Comment
vérifier* — qui est bonne et se conserve.

**Ajouts :** INV-19 à INV-23 de la DP Impacts, une fois celle-ci approuvée.

**Une entrée gagne un contenu qu'elle n'a pas :** INV-14 passe de « rien ne le
protège » à la description de `Statistic.astro` et de ses trois états.

### 3.7 `docs/migration/REVIEW_CHECKLIST.md` — **réécrire, renommer, conserver**

**Nouveau chemin :** section de `docs/GOVERNANCE.md`.

**Justification de la fusion plutôt que du fichier séparé.** La checklist *est*
la procédure de revue. Séparer « comment on décide » de « comment on relit »
produit deux fichiers qu'on lit toujours ensemble. Si la section devient
ingérable, la scinder est un `git mv` — on scindera quand ça fera mal, pas
avant.

**Ce qui est retiré.**

| Point | Motif |
|---|---|
| A1 (`PR-XX.md` existant) | Rejette toute PR ; la machinerie du chantier n'existe plus |
| A2, A3 (fichiers concernés / interdits) | Dépendent des fichiers `PR-XX.md` |
| A5 (fusion de deux PR de la feuille de route) | Plus de feuille de route |
| K10 (retrait des exceptions de jetons) | Les deux exceptions ont été retirées par PR-04 et PR-10 |
| Récapitulatif de fusion, points PR-03 à PR-12 | Protocoles d'un chantier terminé |

**Ce qui est conservé et reste opposable.** B1–B5, C1–C6, D1–D9, E1–E7, F1–F8,
G1–G8, H1–H10, I1–I10, J1–J8, K4–K9, L1–L3, plus la **table de couverture des
invariants**, qui est le meilleur mécanisme du document : *un invariant sans
point de checklist est un invariant déclaré protégé sans l'être*.

**Ce qui est corrigé.** Les 17 renvois « Système §x.y » pointent vers
`docs/DESIGN.md`, dont le plan du §6.4 reprend la numérotation citée, de sorte
que les renvois **résolvent enfin**.

**Ce qui est ajouté.** Points de revue pour INV-19 à INV-23 : `span` vérifié,
analyse absente du bundle du questionnaire, aucun énoncé évaluatif, symétrie
d'exposition, aucune écriture générée dans `content/` sans relecture.

### 3.8 `docs/impacts/DECISION.md` — **déplacer, renommer**

**Nouveau chemin :** `docs/decisions/DP-IMPACTS.md`.

**Justification.** Le nom `DECISION.md` ne dit ni de quoi il décide ni son genre.
Le placer dans `docs/decisions/` le range avec le registre, dont il est le
prolongement : il porte DP-29→39, DT-21→29 et INV-19→23.

**Anti-duplication.** Ses décisions **ne sont pas recopiées** dans le registre.
Le registre les liste par identifiant avec un renvoi. Règle générale :
*une décision documentée en détail ailleurs figure au registre comme entrée
d'index, jamais comme copie.*

**Cycle de vie.** À l'implémentation, la DP se scinde :

| Contenu | Destination finale |
|---|---|
| Décisions DP-29→39, DT-21→29 | `docs/decisions/` — permanent, immuable |
| Invariants INV-19→23 | `docs/INVARIANTS.md` |
| Schéma JSON, vocabulaire des groupes | `content/README.md` |
| Prompts, règles du linter | Docstrings de `pipeline/impacts.py` et `pipeline/neutrality.py` — **au plus près du code qui les exécute**, jamais en double |
| Règles UX U-01→U-13 | `docs/DESIGN.md` |
| Critères d'acceptation A-1→A-18 | Description de la PR, puis disparaissent |

### 3.9 Ce qui n'est pas créé, et pourquoi

Trois documents attendus **ne seront pas écrits**. C'est une décision, pas un
oubli.

| Document | Motif du refus |
|---|---|
| `docs/METHODOLOGY.md` | **La méthodologie publique existe déjà : c'est `/fr/method/`**, rendue depuis `ui.js`. Un fichier Markdown parallèle serait une copie qui diverge — exactement ce que K9 et INV-07 interdisent pour les données. `ARCHITECTURE.md` renvoie à la page ; il ne la double pas |
| `docs/PIPELINE.md` | Les cinq modules de `pipeline/` portent des docstrings qui expliquent le *pourquoi*, pas seulement le *quoi*. Un document parallèle vieillirait plus vite que le code. `ARCHITECTURE.md` décrit la chaîne en dix lignes et renvoie aux modules |
| `docs/adr/` | Le dépôt possède déjà un genre de décision — DP/DT — avec un format éprouvé sur 48 entrées. Introduire les ADR créerait **deux genres pour une même chose** et poserait, à chaque décision, la question de savoir lequel employer. Voir la question ouverte Q-2 |

---

## 4 — Architecture documentaire cible

```
README.md                      public — ce que c'est, démarrer, où lire quoi
CLAUDE.md                      instructions d'agent
content/README.md              schéma de contenu + garanties CI (fait foi)

docs/
  ARCHITECTURE.md              PERMANENT  les quatre domaines, la chaîne, le glossaire
  PRINCIPLES.md                PERMANENT  P1–P10 + philosophie du produit
  INVARIANTS.md                PERMANENT  INV-01 → INV-23
  DESIGN.md                    PERMANENT  le système d'interface (enfin écrit)
  AI.md                        PERMANENT  la doctrine du modèle de langage
  GOVERNANCE.md                PERMANENT  décider, relire, conventions, cycle de vie

  decisions/                   HISTORIQUE — immuable
    REGISTRY.md                DP-01 → DP-39, DT-01 → DT-29 (index + entrées)
    DP-IMPACTS.md              la DP de la fonctionnalité Impacts

  wip/                         TEMPORAIRE — supprimé à la livraison
    AUDIT-DOCUMENTAIRE.md      ce fichier
```

**Volume.** 8 fichiers → 11, mais **4 039 lignes → ≈ 3 100**, dont zéro ligne
fausse. Les 1 016 lignes du registre et les 1 333 de la DP dominent le total et
sont toutes utiles ; ce qui disparaît, ce sont les 500 lignes de planification
périmée.

**Trois tiers, trois règles de lecture.**

| Tier | Question à laquelle il répond | Peut-on le modifier ? |
|---|---|---|
| **Permanent** — `docs/*.md` | *Comment le projet est-il, aujourd'hui ?* | Oui, **dans la PR qui rend la phrase fausse** |
| **Historique** — `docs/decisions/` | *Pourquoi en est-on arrivé là ?* | **Non.** On ajoute une décision qui remplace |
| **Temporaire** — `docs/wip/` | *Que sommes-nous en train de faire ?* | Oui, et il est **supprimé** à la fin |

---

## 5 — Politique de cycle de vie

### 5.1 Règles

**R-1 — Tout document temporaire porte son acte de décès en première ligne.**

```
**Statut : temporaire.** Supprimé par la PR qui livre <X>.
**Créé le :** AAAA-MM-JJ.
```

Un document de `docs/wip/` sans cet en-tête est un défaut : il est déplacé ou
supprimé sans discussion.

**R-2 — La suppression appartient à la PR qui livre.** Le document de travail
disparaît dans le même commit que le dernier élément du chantier qu'il décrit.
Reporter la suppression à « plus tard » est exactement le mécanisme qui a produit
la situation auditée ici.

**R-3 — Rien ne quitte `docs/wip/` sans passer par le sas.** Avant suppression,
le contenu destiné à survivre est **déplacé** vers un document permanent. La
table de sauvetage du §7 est le modèle : une ligne par fragment, sa destination.

**R-4 — Péremption automatique.** Un document de `docs/wip/` dont la date de
création remonte à plus de **six mois** est supprimé sans revue. S'il était
encore utile, il aurait été promu.

**R-5 — Un document permanent n'est jamais annoté « obsolète ».** Il est corrigé
dans la PR qui le rend faux, ou supprimé. Une note « cette section n'est plus à
jour » est le pire des trois états : elle laisse le lecteur décider quelles
phrases croire.

**R-6 — Le tier historique est en écriture seule.** Une décision se remplace par
une décision. `Remplace :` / `Remplacée par :` en tête. Aucune réécriture sur
place, aucune suppression.

**R-7 — Aucun numéro de ligne dans un document permanent.** On cite un fichier
et un symbole. Le §2.4 mesure ce que coûte l'infraction.

**R-8 — Une garantie énoncée dans un document permanent est exécutable.** Si une
phrase affirme qu'une propriété tient, elle nomme le test, le contrôle ou le
point de revue qui la fait tenir. Sinon la phrase est retirée. C'est P1 appliqué
à la documentation elle-même.

### 5.2 Application immédiate

| Document | Sort selon la politique |
|---|---|
| `docs/wip/AUDIT-DOCUMENTAIRE.md` | Supprimé par la PR de réorganisation |
| `docs/decisions/DP-IMPACTS.md` | Scindé à l'implémentation (§3.8), puis conservé comme décision |
| `docs/migration/*` | Éclatés (§7) puis supprimés — **après** le commit correctif de `.gitignore` |

---

## 6 — Plan de contenu des documents à créer

### 6.1 `docs/ARCHITECTURE.md` — permanent

| Section | Origine | Volume |
|---|---|---|
| Les quatre domaines et pourquoi ils sont séparés | `MIGRATION.md` §3, §4 | 25 l. |
| Où vit la vérité : git vs SQLite | `CLAUDE.md`, DP-06 | 10 l. |
| La chaîne de build et ce que la CI exécute | `pages.yml`, `daily.yml` | 20 l. |
| L'API : deux endpoints, une table, la frontière de confiance | `MIGRATION.md` §9 | 25 l. |
| **Métriques du corpus, datées et recalculables** | `MIGRATION.md` §8 | 35 l. |
| Contraintes de sécurité | `MIGRATION.md` §17 | 20 l. |
| **Glossaire** — aveuglement, formation, proposition, couverture, base de comparaison, appareil, registre, effectif | `MIGRATION.md` §30 | 30 l. |
| Manques connus : OQ-03, OQ-04, duplication D5 | `MIGRATION.md` §31, §10 | 15 l. |
| Renvois : méthodologie publique, modules du pipeline | — | 5 l. |

**Point de vigilance.** Les métriques du corpus sont **datées** et portent la
mention de la commande qui les recalcule. Elles justifient DP-11, DP-26 et
DP-27 : si elles changent sans que ces décisions soient réexaminées, trois
justifications deviennent fausses en silence.

### 6.2 `docs/PRINCIPLES.md` — permanent

**Partie A — Les dix principes.** P1 à P10, repris **verbatim** de
`MIGRATION.md` §12. Ils sont normatifs, ils sont cités dans le code et dans la
checklist, ils sont exacts. Aucune réécriture.

**Partie B — Philosophie de Civis.**

La trajectoire, énoncée explicitement :

> **À l'origine :** présenter fidèlement les programmes.
> **À terme :** aider les citoyens à comprendre les programmes sans jamais leur
> dire quoi penser.

Puis la **hiérarchie des sources**, qui est la forme opérationnelle de cette
philosophie :

| Niveau | Nature | Vérifiable par | Peut remplacer le niveau au-dessus |
|---|---|---|---|
| 1 | **Document officiel** | son empreinte SHA-256 | — |
| 2 | **Citation** | `pipeline.check`, mot pour mot | **Non** |
| 3 | **Notre reformulation** | relecture humaine, déclarée comme telle | **Non** |
| 4 | **Explication générée** | `span` verbatim pour les faits ; rien pour les inférences | **Non** |

> **Règle unique :** un niveau **accompagne** le niveau au-dessus de lui, il ne
> s'y substitue jamais. Une explication à côté d'une citation est une aide ;
> une explication à la place d'une citation est une réécriture du document.

Puis les huit rappels, énoncés comme interdits et non comme intentions :

1. Le document officiel reste la source primaire.
2. Toute génération est secondaire et dérivée.
3. Une explication ne remplace jamais une citation.
4. Les inférences sont distinguées des faits **par la preuve**, pas par une
   étiquette.
5. Aucune recommandation politique.
6. Aucune personnalisation politique.
7. Aucune prédiction électorale.
8. Aucune évaluation normative des mesures.

**Partie C — Doctrine de neutralité.** Le principe qui gouverne tout le reste :

> **Une garantie de neutralité qui repose sur la bonne volonté de quelqu'un —
> nous, un relecteur, un modèle — n'est pas une garantie. Une garantie de
> neutralité est un programme qui échoue.**

Décliné en quatre mécanismes existants : aveuglement structurel, vérification
verbatim, vocabulaires fermés (thèmes, groupes, échelle), interface achromatique.
Chacun rend une faute **impossible plutôt qu'improbable**.

### 6.3 `docs/AI.md` — permanent, indépendant du fournisseur

Le document que le brief demande. **Aucun nom de fournisseur dans les huit
premières sections** ; le fournisseur retenu apparaît en dernière section, comme
détail d'implémentation daté.

**§1 — Pourquoi un modèle de langage.** Le corpus est du texte non structuré :
des PDF de programmes de plusieurs centaines de pages. L'alternative est la
saisie manuelle intégrale. Le modèle fait de la **transformation de texte sous
contrainte**, jamais de la production de connaissance. Ce qu'il apporte est du
débit de lecture, pas du savoir.

**§2 — Pourquoi un modèle n'est jamais une source de vérité.** Parce qu'il n'a
pas de provenance. La source de vérité est le document officiel et son empreinte.
Une sortie de modèle est un **candidat** ; un candidat devient un fait lorsqu'il
est rattaché à un fragment vérifiable ou validé par un humain qui en prend la
responsabilité.

**§3 — Ce qu'on peut lui confier.** Reformuler un extrait en question fermée ;
proposer une catégorisation dans un vocabulaire fermé ; proposer un fragment
candidat ; traduire ; signaler une violation dans un texte.

> **Le test d'admissibilité, unique :** *la sortie peut-elle être vérifiée mot
> pour mot par une machine, ou contrainte à une énumération finie, ou relue par
> un humain en moins d'une minute ?* Trois « non » : la tâche ne relève pas du
> modèle.

**§4 — Ce qu'on ne lui confie jamais.** Décider qu'un contenu est publiable ;
attribuer une position à une formation ; produire un chiffre ; produire un
jugement ; écrire dans `content/` ; s'exécuter pendant une visite ; arbitrer une
décision de conception.

**§5 — D'où vient la neutralité : quatre couches, aucune dans le modèle.**

| Couche | Mécanisme | Survit à un changement de modèle |
|---|---|---|
| Aveuglement du générateur | l'identité de la formation n'entre pas dans le prompt (DP-35) | **Oui** — propriété du code appelant |
| Vérification verbatim | `pipeline.check`, citations et `span` (INV-06, INV-19) | **Oui** — porte sur le contenu |
| Linter déterministe | `pipeline/neutrality.py`, en CI (INV-21) | **Oui** — porte sur le contenu |
| Relecture humaine | seule écriture autorisée dans `content/` (INV-23) | **Oui** |

**§6 — Pourquoi la neutralité ne repose jamais sur le modèle.** Un modèle est
opaque, mis à jour sans notre accord, et son alignement est le produit des choix
d'un tiers.

> **Une propriété garantie par un fournisseur est une propriété que le
> fournisseur peut retirer, sans préavis et sans que nous le sachions.**

Corollaire opérationnel : toute garantie doit être **réexécutable sur le contenu
commité, sans le modèle**. C'est le critère qui décide si un mécanisme de
neutralité est acceptable.

**§7 — Le rôle de chaque acteur.**

| Acteur | Rôle | Autorité |
|---|---|---|
| **Citation** | Ancrage. Le seul élément dont la vérité ne dépend d'aucun de nos choix | Fait foi |
| **CI** | Exécute les garanties, en continu, sur le contenu commité, sans savoir qui l'a produit | Bloque |
| **Linter** | Garantie déterministe, reproductible, lisible, opposable. C'est lui qui rend un changement de fournisseur sûr | Bloque |
| **Audit LLM** | Attrape le contextuel qu'un lexique ne voit pas. **Annote, ne bloque jamais seul** | Signale |
| **Relecture humaine** | Prend la responsabilité éditoriale. Seule autorisée à écrire dans `content/` | Décide |

**§8 — Reproductibilité, versionnement, régénération, traçabilité.**

*Reproductibilité.* Énoncé honnête : **une génération n'est pas reproductible**,
et nous ne le promettons pas. Ce qui est reproductible est la **vérification** :
n'importe qui peut rejouer `pipeline.check` sur le contenu commité et obtenir le
même verdict, sans clé d'API et sans modèle.

*Ce qui est versionné.* Le prompt (constante dans le code, donc dans git) ; le
schéma de sortie ; le nom du modèle (champ `model` par entrée) ; la date de
relecture (`reviewed`) ; le contenu ; l'empreinte du document source.

*Ce qui n'est pas versionné, et pourquoi.* Pas d'empreinte de prompt par entrée :
`reviewed` date l'entrée, l'historique git date le prompt, leur croisement donne
le prompt en vigueur. Un hash par entrée ajouterait du bruit de diff à chaque
retouche de formulation pour une information déjà déductible.

*Évolution des modèles.* Un changement de modèle **ne périme aucun contenu
relu** : ce contenu a été validé par un humain, pas par le modèle. Le champ
`model` rend le changement visible en diff. Une régénération de masse est une
**décision documentée**, jamais une conséquence automatique d'une sortie de
modèle.

*Quand régénérer — trois cas, et aucun autre.*
1. La citation source a changé (`of` ne correspond plus).
2. Un `span` n'est plus retrouvé verbatim dans le document.
3. Une décision documentée l'exige — nouveau vocabulaire, nouvelles bornes,
   nouveau prompt jugé substantiellement différent.

> **« Un meilleur modèle est sorti » n'est pas un motif de régénération.**
> Régénérer sans motif remplace du contenu relu par du contenu non relu.

*Traçabilité d'un contenu généré.* Chaque entrée répond à quatre questions :
de quoi elle dérive (`of`), par quel modèle (`model`), quand un humain l'a
validée (`reviewed`), et sur quel fragment repose chaque affirmation factuelle
(`span`). L'historique git fournit le cinquième élément : le prompt en vigueur à
cette date.

**§9 — Le fournisseur retenu.** Section **datée**, isolée, remplaçable.

Contenu : le fournisseur en vigueur, les motifs du choix (API publique, palier
gratuit, performances, style moins normatif d'après les évaluations publiques),
et les quatre rappels demandés :

1. C'est un **choix d'implémentation**, pas une décision d'architecture.
2. La neutralité ne dépend jamais du fournisseur (§5, §6).
3. Les garanties viennent du pipeline de validation.
4. Le fournisseur pourra être remplacé.

Plus **la seule chose vraiment utile de cette section** : la liste exhaustive des
points du dépôt où le fournisseur est nommé, de sorte qu'un remplacement se
mesure au lieu de se deviner.

| Point de couplage | Fichier |
|---|---|
| Dépendance | `pipeline/requirements.txt` |
| Client et appel par lots | `pipeline/generate.py`, futur `pipeline/impacts.py` |
| Nom du modèle | constante `MODEL` |
| Variable d'environnement de la clé | `generate.py`, `README.md` |
| Forme du schéma de sortie | constante `SCHEMA` |

**Cinq points.** C'est le coût réel d'un changement de fournisseur, et c'est
l'argument concret de DT-29 contre une couche d'abstraction.

### 6.4 `docs/DESIGN.md` — permanent

Le « système d'interface » cité 17 fois et jamais écrit. **Il n'est pas rédigé
de zéro** : `MIGRATION.md` §15 et §16 en contiennent l'extrait opérationnel, et
c'est cet extrait qui est promu au rang de document, avec la numérotation que la
checklist cite déjà.

| § | Contenu | Origine |
|---|---|---|
| 1.3 | Aucun élément décoratif sans fonction | §15 |
| 3.1 | Familles : sans pour notre texte, sérif **exclusivement** pour le cité | §15 |
| 3.2 | Échelle de taille — six valeurs | §15 |
| 3.3 | Graisses 400/600 ; la graisse ne change jamais selon un état | §15 |
| 3.5 | Espacements — cinq valeurs | §15 |
| 3.7 | **Les registres de provenance et la règle d'économie du marquage** | §15 |
| 5.2 | Lexique : « enregistrement », jamais « carte » | §15 |
| 5.3 | L'échelle de réponse ne se replie à aucune largeur | §16 |
| 7.3 | Cibles 44×44 px | §16 |
| 7.8 | Régions vivantes mesurées | §16 |
| 8.1–8.4 | Rédaction : « nous »/« vous », auto-qualification, dates absolues, termes techniques | §15, checklist I1–I9 |
| — | Palette achromatique, focus double, animations, mesure | §15 |
| — | **U-01 → U-13** : les règles UX de la fonctionnalité Impacts | DP Impacts §11 |

**Modification requise par la fonctionnalité Impacts.** Le §3.7 décrit
**quatre** registres. L'explication générée en constitue un **cinquième** —
notre déduction — distinct de notre commentaire méthodologique parce qu'il porte
sur une mesure précise et qu'il coexiste, dans le même bloc, avec la citation
qu'il commente. La règle U-11 de la DP en découle.

### 6.5 `docs/GOVERNANCE.md` — permanent

| Section | Contenu |
|---|---|
| **Comment une fonctionnalité est conçue** | Analyse → DP → approbation → découpage → implémentation. C'est la séquence effectivement suivie pour Impacts ; elle est écrite parce qu'elle a marché |
| **Quand une DP est nécessaire** | Voir la règle ci-dessous |
| **Quand une entrée de registre suffit** | Décision locale, réversible, sans effet sur ce que voit l'utilisateur avant la révélation |
| **Quand un changement doit être documenté** | *Si le changement rend fausse une phrase d'un document permanent, la PR corrige le document.* Sinon, rien. Aucune obligation de journal |
| **Comment une décision est remplacée** | R-6 : nouvelle entrée, `Remplace :` / `Remplacée par :` |
| **Invariants incassables** | Renvoi à `INVARIANTS.md` + la méta-règle : une PR qui casse un invariant est rejetée **avant** l'examen de ses mérites |
| **Préserver la neutralité dans le temps** | Les mécanismes exécutables, et la règle : toute nouvelle garantie de neutralité doit être un programme, pas une phrase |
| **Conventions** | INV-15 (contenu français, code anglais) ; aucune dépendance npm (DT-01) ; commentaires `ponytail:` pour les simplifications assumées ; JSON canonique (DT-25) ; messages de commit en anglais |
| **Checklist de revue** | Les 37 points conservés du §3.7, plus ceux d'Impacts |
| **Vérifications manuelles M1–M8** | Reprises de `MIGRATION.md` §27, toujours valides |
| **Cycle de vie documentaire** | R-1 à R-8 du §5 |

**Règle proposée — quand une DP est requise.** Une DP est nécessaire si le
changement touche **au moins un** de ces cinq points :

1. un invariant, ou en crée un ;
2. la neutralité — ce qui est affiché, dans quel ordre, avec quelle
   qualification ;
3. le modèle de données de `content/` ;
4. le rôle ou le périmètre du modèle de langage ;
5. ce que l'utilisateur voit **avant** la révélation.

Sinon : une entrée de registre, ou rien. **Une DP pour un changement de style de
bordure est du cérémonial ; le cérémonial finit par n'être plus lu.**

---

## 7 — Table de sauvetage avant suppression

Ce qui doit être **déplacé** hors de `docs/migration/` avant que le dossier
disparaisse. Rien de cette table n'existe ailleurs.

| Fragment | Source | Destination | Motif |
|---|---|---|---|
| P1–P10 | `MIGRATION.md` §12 | `PRINCIPLES.md` A | Normatifs, cités dans le code |
| Contexte et hypothèses du projet | §3 | `ARCHITECTURE.md` | Mainteneur unique, site complet sans API |
| Les quatre domaines, chaîne de build | §4 | `ARCHITECTURE.md` | — |
| **Métriques du corpus** | §8 | `ARCHITECTURE.md` | **Justifient DP-11, DP-26, DP-27** |
| Description de l'API et frontière de confiance | §9 | `ARCHITECTURE.md` | Seule description existante |
| Duplication D5 (`THEMES` en double) | §10 | `ARCHITECTURE.md` › manques | **Non résolue** |
| Contraintes de conception | §15 | `DESIGN.md` §1–§8 | Résout 17 renvois cassés |
| Contraintes d'accessibilité | §16 | `DESIGN.md` §7 | — |
| Contraintes de sécurité | §17 | `ARCHITECTURE.md` | — |
| Maintenabilité, réversibilité, revue | §19–§21 | `GOVERNANCE.md` | — |
| **M1–M8** | §27 | `GOVERNANCE.md` | Toujours utiles à toute PR d'interface |
| Glossaire | §30 | `ARCHITECTURE.md` | Fixe le lexique opposable par I6 |
| OQ-03, OQ-04 | §31 | `ARCHITECTURE.md` › manques | **Toujours ouverts** |
| 37 points de checklist | `REVIEW_CHECKLIST.md` | `GOVERNANCE.md` | — |
| Table de couverture des invariants | `REVIEW_CHECKLIST.md` | `GOVERNANCE.md` | Mécanisme le plus utile du document |

**Ne sont pas sauvés** — et disparaissent avec le dossier : §1, §2, §5, §6, §7,
§10 (hors D5), §11, §13, §14, §18, §22, §23, §24, §25, §26, §28, §29, OQ-08, et
la machinerie de PR de la checklist. Environ **560 lignes**, toutes descriptives
d'un état ou d'un plan qui n'existent plus.

---

## 8 — Conséquences sur la DP Impacts

L'annonce du passage à Gemini a des effets que la DP, écrite sans cette
information, ne couvre pas. Aucun n'invalide la conception ; trois demandent une
retouche.

**8.1 — Ce qui ne bouge pas.** DT-29 (aucune abstraction de fournisseur, un
point d'appel unique `run_batch()`) et INV-21 (le linter porte la garantie, pas
le prompt) ont été écrits exactement pour cette situation. La conception résiste
au changement de fournisseur, ce qui était l'objectif.

**8.2 — Trois retouches nécessaires.**

| # | Point | Retouche |
|---|---|---|
| 1 | DP §5.4/§5.5 emploie `additionalProperties: false` et un schéma JSON strict, propre à l'API actuelle. Les schémas de sortie structurée diffèrent d'un fournisseur à l'autre — plusieurs n'acceptent qu'un sous-ensemble d'OpenAPI | Énoncer le schéma comme **contrat logique**, et poser que sa traduction dans le dialecte du fournisseur est une affaire d'implémentation. **Le linter reste la couche opposable** — ce que la DP dit déjà pour les conditionnalités ; l'étendre à tout le schéma |
| 2 | L'exemple de contenu du §5.1 porte `"model": "claude-opus-5"` | Remplacer par une valeur générique dans l'exemple. Le champ reste, sa valeur est celle du modèle réellement employé |
| 3 | La DP suppose une API de traitement par lots avec récupération asynchrone | `run_batch()` absorbe déjà un fournisseur sans lots par une boucle synchrone. **À écrire explicitement** dans DT-29 plutôt qu'à déduire |

**8.3 — Trois risques opérationnels à documenter, propres au contexte.**

1. **Filtrage de sécurité sur du contenu politique.** Les programmes portent de
   l'immigration, de la sécurité, de la fiscalité. Un fournisseur peut refuser
   de traiter un extrait, ou renvoyer une sortie tronquée. Le pipeline doit
   traiter un refus comme un **échec explicite consigné**, jamais comme un point
   sans analyse silencieux — c'est INV-14 appliqué au pipeline, et le précédent
   existe (`fetch.py` distingue déjà l'hôte injoignable du document jamais
   récupéré). **À ajouter comme critère d'acceptation.**
2. **Palier gratuit et usage des données.** Le contenu envoyé est du texte de
   programme public, donc aucun enjeu de vie privée. Mais si les conditions du
   palier gratuit autorisent la réutilisation des requêtes, cela mérite d'être
   **énoncé** dans `AI.md` plutôt que découvert — P2 et P5 s'appliquent au
   dépôt autant qu'à l'interface.
3. **Quotas.** Un palier gratuit implique des limites de débit. La génération
   incrémentale (DT-24) et `--limit N` les absorbent déjà ; il faut simplement
   que l'échec de quota soit distinguable d'un échec de contenu.

**8.4 — Une opportunité.** Le passage à Gemini est le **premier test grandeur
réelle** de DT-29 et d'INV-21. S'il se fait en touchant les cinq points de
couplage du §6.3 et rien d'autre, la thèse « les garanties viennent du pipeline,
pas du fournisseur » cesse d'être une affirmation. Cela mérite d'être mesuré et
consigné dans `AI.md` §9.

---

## 9 — Risques

| # | Risque | Gravité | Atténuation |
|---|---|---|---|
| R-1 | **Supprimer `docs/migration/` avant de corriger `.gitignore` détruit définitivement 2 415 lignes**, dont 48 décisions et 18 invariants | **Critique** | Prérequis absolu du §0 : corriger et commiter d'abord. Aucune suppression avant |
| R-2 | Le sas de sauvetage (§7) perd un fragment en route | Élevée | La table est exhaustive et vérifiable ligne à ligne ; la PR de suppression cite la table dans sa description |
| R-3 | La réorganisation devient l'occasion de « réécrire un peu » le registre | Élevée | R-6 : le tier historique est en écriture seule. Le toilettage du §3.5 est **limité à trois opérations nommées** |
| R-4 | `DESIGN.md` promeut au rang de norme un extrait qui n'était qu'un extrait, et fige des règles jamais complètement écrites | Moyenne | Assumé : **une norme incomplète mais lisible vaut mieux que 17 renvois vers rien**. Ce qui manque se constate en revue et s'ajoute |
| R-5 | `AI.md` vieillit au premier changement de fournisseur | Moyenne | §1–§8 ne nomment aucun fournisseur ; seul §9 est daté et remplaçable. C'est la structure qui porte la longévité |
| R-6 | Onze fichiers au lieu de huit : la documentation devient un labyrinthe | Moyenne | La section « Où lire quoi » du README est la porte unique. Trois tiers, trois répertoires, une règle de lecture chacun |
| R-7 | Les métriques du corpus se périment silencieusement et invalident DP-11, DP-26, DP-27 | Moyenne | Elles sont **datées** et portent leur commande de recalcul. Un test qui les vérifie était déjà « recommandé » par `MIGRATION.md` §28 et n'a jamais été écrit — **c'est la seule dette de test que cette réorganisation devrait solder** |
| R-8 | La checklist reste théorique faute de PR à relire | Faible | La PR d'implémentation d'Impacts en est le premier usage réel |

---

## 10 — Questions restantes

**Q-1 — `.gitignore`. Résolue.** La règle `*.md` est retirée. Reste à commiter
`docs/` et `CLAUDE.md` avant toute suppression — mais après avoir répondu à Q-8,
qui est le vrai point de non-retour.

**Q-2 — ADR.** Ma recommandation est de **ne pas introduire les ADR** : le genre
DP/DT existe, il est éprouvé sur 48 entrées, et un second genre poserait à
chaque décision la question de savoir lequel employer. Si tu veux malgré tout
les ADR, la conversion propre est de renommer le registre et de reclasser les 48
entrées — pas de faire cohabiter les deux. Tu confirmes le refus ?

**Q-3 — Le registre : un fichier ou un par décision ?** Je propose **un seul
fichier** (`REGISTRY.md`, 1 016 lignes). Un fichier par décision donnerait 50
fichiers pour un dépôt de 57 fichiers suivis — la documentation pèserait autant
que le code. Tu confirmes ?

**Q-4 — Fusion checklist + gouvernance.** Je propose de fusionner
`REVIEW_CHECKLIST.md` dans `GOVERNANCE.md`. Le fichier fera environ 250 lignes.
Préfères-tu deux fichiers séparés ?

**Q-5 — La méthodologie publique.** Je propose de **ne pas** créer de
`METHODOLOGY.md` : la méthodologie est la page `/method/`, et un doublon
Markdown divergerait. Confirmes-tu qu'aucun besoin ne réclame une version
Markdown ?

**Q-6 — Sort de `docs/migration/`.** Suppression pure après sauvetage, ou
déplacement vers `docs/decisions/archive/` ? Ma recommandation est la
**suppression** : une fois `.gitignore` corrigé et le dossier commité une fois,
l'historique git *est* l'archive, et un dossier `archive/` en vue invite à le
consulter alors que son contenu est faux.

**Q-7 — Le test des métriques du corpus.** Faut-il l'écrire dans cette phase
(R-7) ? Il est court — il relit `content/` et compare à quatre chiffres — et il
protège trois décisions. Il déborde du périmètre documentaire, d'où la question.

**Q-8 — Publication.** Une fois `docs/` versionné, il devient public avec le
dépôt. Le registre contient des formulations franches sur les défauts du produit
(déséquilibre du corpus, score sensible à la couverture, échantillon
auto-sélectionné). C'est cohérent avec P5 et P10, et je le recommande. Mais
c'est une décision de publication, et elle t'appartient.

---

**Fin de l'audit.** Aucune modification n'a été apportée. La suite attend ton
arbitrage sur Q-1 à Q-8, et en particulier sur Q-1, qui bloque tout le reste.
