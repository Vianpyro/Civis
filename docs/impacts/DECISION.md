# Civis — Decision Proposal : conséquences concrètes d'une mesure

**Objet.** Référence normative de la fonctionnalité « conséquences d'une mesure ».
Un développeur qui implémente à partir de ce document ne doit avoir **aucune
décision de conception à prendre**. S'il en rencontre une, c'est un défaut de
cette DP : il s'arrête et la signale, il ne tranche pas.

**Portée.** Ce document fixe la conception. Il ne contient **pas** de découpage
en PR ni de plan d'implémentation : ils vivent dans
`docs/impacts/ROADMAP.md`, approuvé le 2 août 2026.

**Amendements.** Quatre décisions ont été ajoutées après approbation, au §17 :
**DP-40** (corpus pilote), **DT-30** (suite de tests Python), **DT-31**
(configuration du fournisseur), **DT-32** (rapport agrégé de W-02 et deux
contrôles de schéma opposables, critère A-19). Elles amendent DT-24, DT-26,
DT-29, W-02 et le critère A-4, qui portent chacun un renvoi à l'endroit concerné. Le corps du
document n'a pas été réécrit : un amendement daté se lit, une réécriture
silencieuse se subit.

**Format.** Celui de `docs/migration/DECISIONS.md`. La numérotation prolonge le
registre existant : DP-29…DP-39, DT-21…DT-29, INV-19…INV-23.

**Règle d'usage.** Aucune décision de ce document ne se réinterprète. Une session
qui pense qu'une décision est mauvaise ne la modifie pas : elle le signale et
s'arrête.

---

## Sommaire

1. [Énoncé de la fonctionnalité](#1--énoncé-de-la-fonctionnalité)
2. [Questions ouvertes — toutes résolues](#2--questions-ouvertes--toutes-résolues)
3. [Décisions produit — DP-29 à DP-39](#3--décisions-produit)
4. [Décisions techniques — DT-21 à DT-29](#4--décisions-techniques)
5. [Schéma JSON final](#5--schéma-json-final)
6. [Vocabulaire fermé des groupes concernés](#6--vocabulaire-fermé-des-groupes-concernés)
7. [Invariants — INV-19 à INV-23](#7--invariants)
8. [Rôles : LLM, linter, relecture humaine](#8--rôles--llm-linter-relecture-humaine)
9. [Prompts normatifs](#9--prompts-normatifs)
10. [Règles du linter déterministe](#10--règles-du-linter-déterministe)
11. [Règles UX finales](#11--règles-ux-finales)
12. [Fichiers concernés](#12--fichiers-concernés)
13. [Critères d'acceptation](#13--critères-dacceptation)
14. [Non-objectifs](#14--non-objectifs)
15. [Risques résiduels assumés](#15--risques-résiduels-assumés)
16. [Matrice décision → invariant → vérification](#16--matrice-décision--invariant--vérification)
17. [Amendements postérieurs à l'approbation — DP-40, DT-30, DT-31, DT-32](#17--amendements-postérieurs-à-lapprobation)

---

## 1 — Énoncé de la fonctionnalité

Chaque mesure de programme citée sur la page de résultats peut porter une
**analyse descriptive** de ses conséquences, en trois catégories :

- **ce que le texte prévoit** — obligations, droits, restrictions, procédures,
  règles fiscales ou réglementaires que la mesure institue ;
- **qui est concerné** — catégories de personnes et d'organismes, directement ou
  indirectement ;
- **effets attendus** — conséquences concrètes raisonnablement déductibles.

L'analyse est **strictement descriptive**. Elle ne dit jamais si une mesure est
bonne, mauvaise, efficace, coûteuse, opportune ou réalisable.

Elle distingue **structurellement** ce qui est écrit dans le document de ce qui
en est déduit — non par une affirmation, mais par la présence ou l'absence d'une
preuve textuelle vérifiée par la CI.

---

## 2 — Questions ouvertes : toutes résolues

| # | Question | Résolution | Où |
|---|---|---|---|
| 1 | L'analyse s'attache au `point` ou à la `question` ? | Au **`point`** | DP-29 |
| 2 | Quel vocabulaire de groupes pour la France ? | Liste fermée de **22 valeurs**, avec règle de repli sur le niveau de collectivité | DP-32, §6 |
| 3 | Règle « tout ou rien par question » ? | **Oui** | DP-34 |
| 4 | Quels plafonds ? | implication 1–4 · affected 1–5 · effect 0–4 · total 3–10 · `inferred ≤ text` · 200 caractères par énoncé et par langue | DP-33 |
| 5 | Point sans analyse : rien, ou échec CI ? | **Rien d'affiché** (DP-34) ; la CI **avertit**, elle n'échoue pas. Elle n'échoue que sur une entrée *malformée* | DT-26 |
| 6 | Plafond de coût ? | Aucun plafond en dur. Régénération incrémentale + drapeau `--limit N` | DT-24 |
| 7 | Modalité de relecture ? | Identique à celle des questions : JSON dans `review/`, lu avant commit | DP-36, §8 |

Aucune question ouverte ne subsiste. Les points laissés indéterminés par
l'analyse préalable — plafonds, vocabulaire, comportement en couverture
partielle, budget — sont tranchés ci-dessous et ne se rediscutent pas pendant
l'implémentation.

---

## 3 — Décisions produit

### DP-29 — L'analyse s'attache au point de programme, jamais à la question

**Décision.** Une analyse de conséquences est indexée par `point.id`, l'unité
définie dans `content/programs/<élection>/<parti>.json`. Aucune analyse n'est
attachée à une `question`.

**Contexte.** Le modèle offre deux ancres : le point, qui est une mesure réelle
issue d'un document réel et empreint ; la question, qui est une reformulation
aveugle agrégeant jusqu'à quatre formations aux positions opposées.

**Justification.** Trois raisons, par ordre de force.

1. **Vérifiabilité.** Une conséquence dérive d'un texte. Un point a un texte
   source et une empreinte ; une question n'en a pas. Accrocher l'analyse à la
   question produirait de la prose qu'aucune machine ne peut confronter à quoi
   que ce soit — ce que DP-05 et INV-06 refusent pour les citations, et il n'y a
   pas de raison de l'admettre pour un contenu plus inférentiel.
2. **Neutralité.** Écrire « ce que cela implique » pour une question exigerait
   une synthèse inter-formations. C'est exactement là que naissent le cadrage et
   la fausse symétrie.
3. **Cécité.** `content/questions/` est chargé par le questionnaire. Y placer de
   la prose dérivée du programme d'une formation crée une surface de fuite
   lexicale et, plus grave, un cadrage avant la réponse.

**Conséquences.** Le fichier d'analyses est chargé exclusivement par
`results.astro`, comme `programs/` et `positions.json`. Le questionnaire ne le
voit jamais.

**Alternatives rejetées.** Analyse par question, avec sections par formation :
rejetée pour les trois motifs ci-dessus. Analyse par thème : sans ancrage
textuel, c'est de l'éditorial politique.

---

### DP-30 — L'analyse n'apparaît qu'après la révélation

**Décision.** Aucun élément d'analyse — implication, groupe concerné, effet
attendu — n'est affiché ni chargé avant que l'utilisateur ait terminé le
questionnaire.

**Contexte.** L'analyse est du contenu neutre par construction ; la tentation
d'en montrer une partie pendant la passation, « pour aider à comprendre la
question », est réelle.

**Justification.** Exactement le raisonnement de DP-02. Expliquer à quelqu'un ce
qu'une mesure implique avant qu'il ne se positionne, c'est répondre à sa place.
Une analyse neutre reste un cadrage : elle choisit quels effets sont saillants,
et ce choix oriente la réponse. Le produit existe pour retirer le cadrage, pas
pour en substituer un meilleur.

**Conséquences.** Le bloc d'analyse vit dans `#detail` de `results.astro`, sous
la citation de la position. Aucune donnée d'analyse ne transite par le bundle du
questionnaire (INV-20).

**Alternatives rejetées.** Une infobulle « en savoir plus » sur la question
pendant la passation : rejetée, c'est DP-02 contourné par un autre nom.

---

### DP-31 — Trois catégories d'énoncés, deux bases, la preuve est la marque

**Décision.** Chaque énoncé porte :

- un `kind` parmi `implication`, `affected`, `effect` ;
- un `basis` parmi `text` (soutenu par le document) et `inferred` (déduit).

Un énoncé `text` porte obligatoirement un `span` : un fragment **copié à
l'identique** du document source. Un énoncé `inferred` n'en porte jamais.

**Contexte.** Le besoin exprimé est de distinguer « prévu par le texte » de
« simplement attendu ». La solution évidente — un badge — est indisponible :
INV-12 interdit l'information portée par la couleur, et une étiquette textuelle
serait une affirmation de plus, du même statut que celle qu'elle qualifie.

**Justification.** La distinction est **portée par la preuve elle-même**. Un
énoncé textuel affiche son fragment source ; un énoncé déduit n'a rien à
afficher. Le lecteur ne lit pas une étiquette, il constate une présence ou une
absence — et la CI vérifie cette présence mot pour mot (INV-19). C'est le seul
mécanisme du dispositif qui transforme une revendication en propriété vérifiée.

**Conséquences.** `span` devient le pivot de la fonctionnalité. Sa vérification
réutilise la boucle de `check_quotes` (DP-05, INV-06) à quelques lignes près.

**Alternatives rejetées.**
- **Badge coloré** : violerait INV-12 et DP-22.
- **Troisième valeur de `basis`** (« incertain ») ou score de confiance :
  rejetés, le modèle produirait un chiffre qu'il ne peut pas justifier. INV-13
  interdit déjà un nombre sans dénominateur ; un score de confiance en est le cas
  le plus insidieux. L'incertitude est portée par la formulation, dont le
  conditionnel est **rendu obligatoire par le linter** sur tout énoncé `inferred`.

---

### DP-32 — Le groupe concerné est choisi dans un vocabulaire fermé

**Décision.** Un énoncé `kind: "affected"` porte un champ `who` dont la valeur
appartient à la liste fermée du §6, et un champ `directness` valant `direct` ou
`indirect`. Le modèle **choisit** un groupe, il ne le **rédige** jamais.

**Contexte.** « Qui est concerné » est la section où le biais entre le plus
facilement : la caractérisation d'un groupe (« les travailleurs précaires »,
« les familles qui souffrent », « les fraudeurs ») est un acte politique avant
d'être une description.

**Justification.** Un vocabulaire fermé rend cet acte structurellement
impossible. C'est le levier anti-biais le plus efficace de toute la
fonctionnalité, et il apporte l'internationalisation gratuitement : le libellé
est traduit une fois dans `ui.js`, exactement comme `THEMES`.

**Conséquences.** Ajouter une valeur est une décision éditoriale, documentée,
au même titre qu'ajouter un thème. La liste est déclarée deux fois — enum dans
`pipeline/check.py`, libellés dans `web/src/lib/ui.js` — et un contrôle vérifie
que les deux jeux de clés coïncident (DT-27).

**Alternatives rejetées.** Champ libre plafonné à N caractères : rejeté, la
caractérisation tiendrait dans N caractères. Liste ouverte avec validation *a
posteriori* : rejetée, c'est une liste fermée gérée manuellement, en moins
fiable.

---

### DP-33 — Plafonds uniformes et `inferred ≤ text`

**Décision.** Par point, et identiquement pour tous les points :

| Contrainte | Valeur |
|---|---|
| `kind: implication` | 1 à 4 énoncés |
| `kind: affected` | 1 à 5 énoncés |
| `kind: effect` | 0 à 4 énoncés |
| Total | 3 à 10 énoncés |
| Énoncés `inferred` | **≤** nombre d'énoncés `text`, par point |
| Longueur d'un énoncé | ≤ 200 caractères, dans chaque langue |
| Longueur d'un `span` | ≤ 300 caractères |

**Contexte.** Un biais non évident : si les mesures d'une formation reçoivent
neuf énoncés riches et celles d'une autre trois énoncés secs, la page de
révélation avantage la plus verbeuse sans qu'aucune phrase ne soit partisane.
Le volume est un argument.

**Justification.** Des plafonds identiques bornent l'écart par construction,
sans exiger de mesure statistique ni d'équilibrage a posteriori. Le plancher
compte autant que le plafond : il interdit l'analyse squelettique qui
délégitimerait par le vide. `inferred ≤ text` garantit qu'une analyse n'est
jamais majoritairement spéculative.

**Conséquences.** Un point sur lequel on ne peut pas produire au moins une
implication et un groupe concerné, tous deux textuellement soutenus, n'a pas
d'analyse — et par DP-34 la question entière n'en affiche aucune. C'est le mode
d'échec honnête et il est assumé. L'échappatoire n'est pas un assouplissement
du plafond : c'est la relecture humaine, qui peut **écrire ou corriger n'importe
quelle entrée à la main** (DP-36). Le fichier est du contenu, pas une sortie de
générateur.

**Alternatives rejetées.** Contrôle d'écart-type du nombre d'énoncés par
formation : rejeté, complexité de mesure pour un résultat que des bornes fixes
obtiennent directement.

---

### DP-34 — Tout ou rien par question

**Décision.** Le bloc d'analyse d'une question n'est rendu que si **toutes** les
positions de cette question — donc tous les points référencés par
`positions.json` pour cette question — disposent d'une entrée relue. Sinon,
aucune analyse n'est affichée pour cette question, y compris pour les positions
qui en ont une.

**Contexte.** La couverture du corpus est déjà inégale (DP-12, `methodCoverage`)
et cette inégalité est affichée honnêtement. Mais une inégalité *à l'intérieur
d'une même question* est d'une autre nature : le lecteur compare quatre
positions côte à côte, et celle qui porte une analyse paraît documentée face à
celles qui n'en portent pas.

**Justification.** La comparaison est le geste que la page de résultats organise.
Une asymétrie d'exposition dans l'unité de comparaison est un biais direct, non
compensable par un avertissement. Masquer du contenu prêt est un coût réel et
accepté.

**Conséquences.** Le déploiement d'analyses se fait **par question**, jamais par
point isolé. La CI **avertit** sur une question à couverture partielle sans
échouer : une couverture incomplète est l'état normal d'un corpus en cours, pas
une erreur — même doctrine que `check_quotes` qui rapporte « skipped » plutôt
que d'échouer hors ligne.

**Alternatives rejetées.** Afficher ce qui existe avec une mention « analyse non
disponible » sur les autres : rejetée — INV-14 exige qu'une absence s'affiche
comme absence, mais ici l'absence *elle-même* est le biais, et l'annoncer ne le
corrige pas.

---

### DP-35 — Le générateur travaille à l'aveugle

**Décision.** Le prompt de génération ne contient **jamais** l'identité de la
formation : ni identifiant, ni nom, ni sigle, ni le nom du fichier programme, ni
le titre du document source. Il reçoit le thème, la citation et une fenêtre de
contexte documentaire.

**Contexte.** La cécité est jusqu'ici une propriété du client. Rien n'obligeait
à l'étendre au générateur.

**Justification.** C'est l'invariant fondateur appliqué à l'outil qui produit le
contenu. Un modèle qui ignore de quel camp provient une mesure ne peut pas
aligner ses conséquences sur le cadrage habituel de ce camp. Et contrairement à
une consigne de neutralité — invérifiable — l'absence d'une information dans le
prompt est une propriété structurelle, du même ordre que celle qui protège
INV-01 : la page ne peut pas révéler ce qu'elle n'a pas chargé, le modèle ne peut
pas s'aligner sur ce qu'il n'a pas lu.

**Conséquences.** Le `custom_id` de la requête batch est le `point.id`, qui
contient un préfixe de formation (`lr-depense-publique`). Il ne fait pas partie
du prompt et n'est jamais transmis dans le corps du message. L'implémentation
doit s'en assurer explicitement.

**Alternatives rejetées.** Fournir le titre du document « pour le contexte » :
rejeté, le titre porte le nom de la formation.

---

### DP-36 — Deux passes de modèle, un linter, une relecture ; rien n'entre dans `content/` sans humain

**Décision.** Le contenu passe par quatre filtres, dans cet ordre :

1. **Passe 1 — génération** (batch, hors ligne, à l'aveugle) → propose.
2. **Passe 2 — audit** (batch, hors ligne, prompt distinct) → signale.
3. **Linter déterministe** → interdit, à la génération **et en CI**.
4. **Relecture humaine** → décide, seule habilitée à écrire dans `content/`.

Le générateur écrit exclusivement dans `review/`, jamais dans `content/`.

**Contexte.** `generate.py` a déjà cette forme pour les questions. La demande
initiale évoquait « une deuxième passe de validation plutôt qu'une simple
génération ».

**Justification.** Une passe d'audit LLM détecte ce qu'une liste de mots ne
détecte pas — un jugement de valeur contextuel, un `span` qui ne soutient pas
son énoncé. Un linter déterministe détecte ce qu'un LLM laisse passer par
complaisance, et surtout **il s'exécute en CI sur le contenu commité** : la
garantie porte sur le produit, pas sur le producteur. C'est la même doctrine que
`check_quotes`, qui ne fait pas confiance à `generate.py`.

**Conséquences.**
- La passe 2 ne voit **jamais** le prompt de la passe 1. Un auditeur qui connaît
  la règle rationalise sa violation.
- La passe 2 **annote, ne supprime pas**. Le brouillon contient tous les énoncés
  avec leur verdict. Un rejet silencieux masquerait une dérive systématique du
  prompt, qui est précisément ce qu'il faut voir.
- La relecture humaine peut écrire, réécrire ou supprimer n'importe quelle
  entrée. Le fichier est du contenu.

**Alternatives rejetées.** Génération simple + relecture : rejetée, la charge de
relecture explose et l'humain devient le seul filtre. Filtrage automatique des
énoncés non conformes : rejeté, cache la dérive.

---

### DP-37 — Langue : les énoncés suivent l'interface, les fragments restent en français

**Décision.** Les champs `fr`/`en` d'un énoncé sont affichés selon la **langue
d'interface** : `fr` sur `/fr`, `en` sur `/en`. Aucun dispositif d'aide à la
lecture, aucune juxtaposition. Le `span` est affiché **toujours en français**,
avec `lang="fr"`, et n'est jamais traduit.

**Contexte.** DP-18 impose le français comme instrument, l'anglais comme aide à
la lecture, et interdit de substituer une traduction à une citation.

**Justification.** DP-18 protège **l'instrument de mesure** : l'énoncé auquel
l'utilisateur répond doit être le même pour tous (INV-18). Une analyse n'est pas
un instrument, c'est un commentaire — la juxtaposer imposerait une double
lecture pour un gain nul. Le `span`, lui, est un verbatim vérifié par la CI :
une traduction ne serait plus le texte vérifié, donc plus une preuve (INV-06).

**Conséquences.** `reading()` n'est **pas** utilisé pour les énoncés. Le
composant `Quote.astro` est réutilisé tel quel pour le `span` : il porte déjà
`lang={CORPUS_LANG}`, la serif de provenance et le filet vertical.

**Alternatives rejetées.** Juxtaposition fr/en comme pour les questions :
rejetée, allonge un bloc déjà dense sans servir l'instrument.

---

### DP-38 — Le statut épistémique est déclaré sur la page de méthodologie

**Décision.** La page de méthodologie déclare, dans la section des limites : que
les analyses sont produites avec l'assistance d'un modèle de langage ; que les
énoncés marqués comme prévus par le texte sont vérifiés mot pour mot par la CI ;
que les autres sont des déductions non vérifiables ; et que leur nombre ne peut
pas excéder celui des premiers.

**Justification.** P10 : ce qui est vrai dans le dépôt doit être vrai dans
l'interface. DP-17 fixe déjà quatre faits sur le rôle du modèle de langage. Une
fonctionnalité qui produit de l'inférence et ne le déclare pas rend la page de
méthodologie fausse par omission — sur la page dont l'objet est précisément de
ne rien omettre.

**Conséquences.** `methodModelFacts` s'étend ; `methodLimits` reçoit une entrée.
La déclaration porte aussi le fait que les analyses ne sont pas exhaustives.

---

### DP-39 — Périmètre fermé de la fonctionnalité

**Décision.** La liste du §14 énumère ce que cette fonctionnalité ne fera
jamais. Elle est normative. Toute proposition figurant dans cette liste est
refusée sans réexamen, sauf décision explicite du responsable documentée ici.

**Justification.** La pente est courte et régulière : de « ce que cela implique »
vers « est-ce finançable », puis « est-ce constitutionnel », puis « cette
promesse est-elle tenable ». Chaque marche est individuellement défendable et
l'ensemble transforme un questionnaire à l'aveugle en organe d'analyse
politique. Une liste fermée écrite avant la première ligne de code est le seul
mécanisme qui résiste à une bonne raison ponctuelle.

---

## 4 — Décisions techniques

### DT-21 — Fichier satellite `content/impacts/<élection>.json`, indexé par point

**Décision.** Les analyses vivent dans un fichier distinct, indexé par
`point.id`. Elles ne sont **pas** ajoutées comme champ dans
`content/programs/<élection>/<parti>.json`.

**Justification.**
1. `programs/*.json` porte un invariant unique et fort : *toute chaîne
   éditoriale qu'il contient apparaît mot pour mot dans le document source*. Y
   injecter de la prose inférée détruit la possibilité d'énoncer cet invariant
   en une phrase et oblige `check_quotes` à connaître une liste de champs
   exemptés.
2. Les cadences divergent. Les citations sont stables sur des années ; les
   analyses sont régénérées à chaque changement de modèle, de prompt ou de
   vocabulaire. Le bruit de diff polluerait le fichier qui *est* l'argument de
   transparence (DP-06).
3. Le précédent existe : `positions.json` est déjà un satellite indexé par
   identifiant, séparé pour une raison de frontière et non de commodité.

**Conséquences.** Le schéma de contenu passe de trois à quatre familles de
fichiers. `content/README.md` est mis à jour.

**Alternatives rejetées.** Un fichier par formation (`impacts/<élection>/<parti>.json`) :
rejeté, la clé est le point et non la formation ; un fichier unique par scrutin
reste lisible et évite quatre fichiers presque vides.

---

### DT-22 — Une liste plate `items`, pas trois sections typées

**Décision.** L'entrée d'un point contient un tableau unique `items`, chaque
élément portant `kind`. Pas de `{implications: [], affected: [], effects: []}`.

**Justification.** Un seul schéma JSON pour le modèle, une seule boucle de
validation, un seul rendu avec regroupement. Trois sections typées imposeraient
trois schémas, trois boucles et trois branches de rendu pour une information
identique.

**Conséquences.** Le regroupement en trois sections est une opération de rendu.
L'ordre du tableau est canonique (DT-25).

---

### DT-23 — `of` est l'empreinte de la citation, jamais celle du document

**Décision.** Chaque entrée porte `of`, le SHA-256 de la citation du point après
normalisation par `extract.normalise()` puis effondrement des blancs. C'est le
signal de péremption : une entrée est périmée si `of` ne correspond plus, ou si
l'un de ses `span` n'est plus retrouvé verbatim dans le document.

**Justification.** Un PDF réexporté change d'empreinte sans que son texte change.
Indexer sur l'empreinte du document déclencherait une régénération complète à
chaque republication cosmétique — et le workflow `daily.yml` en produit
potentiellement une par jour.

**Conséquences.** Un changement d'empreinte de document seul ne périme rien : il
déclenche déjà l'ouverture d'une PR de relecture des questions, et la
vérification des `span` en CI signalera tout décrochage réel.

**Alternatives rejetées.** `of` = empreinte du document : rejeté ci-dessus.
Aucun champ `of` (comparaison par relecture) : rejeté, la régénération
incrémentale devient impossible.

---

### DT-24 — Une requête batch par point ; portée limitée aux points affichés

**Décision.** Une requête de passe 1 et une requête de passe 2 par point.
Les points générés sont **uniquement** ceux référencés par `positions.json`.
Un drapeau `--limit N` plafonne le nombre de points traités par exécution ;
`--force` régénère sans tenir compte de `of`.

**Justification.** Le découpage par point donne la régénération incrémentale,
l'échec indépendant et l'absence de contamination de contexte entre mesures de
formations différentes — cette dernière propriété est requise par DP-35. Un
point jamais affiché n'a pas besoin d'analyse.

**Conséquences.** Coût d'un premier passage complet à 120 points : environ 240
requêtes courtes en batch, hors ligne, sans contrainte de latence. En régime
stable : zéro appel. Le cache **est** le fichier commité — aucune couche de
cache à construire, conformément à DP-06.

> **Amendé par DP-40 (§17).** Le premier passage ne porte pas sur les 120 points
> mais sur un corpus pilote. La décision ci-dessus est inchangée sur le fond :
> une requête par point, portée limitée aux points affichés.

---

### DT-25 — Le fichier est canonique ; la CI échoue sur une réécriture divergente

**Décision.** `content/impacts/<élection>.json` a une forme canonique : clés de
points triées, `items` triés par `kind` dans l'ordre `implication`, `affected`,
`effect` (ordre d'apparition préservé à l'intérieur d'un `kind`), indentation de
deux espaces, `ensure_ascii=False`, saut de ligne final. `check` sérialise à
nouveau le contenu chargé et échoue si le résultat diffère octet à octet du
fichier lu.

**Justification.** Un contrôle d'une ligne qui supprime définitivement toute
divergence de mise en forme entre une régénération machine et une correction
manuelle. Sans lui, les diffs de régénération deviennent illisibles et la
relecture — qui est le filtre le plus important du dispositif — se dégrade.

---

### DT-26 — Le linter est un module unique, appelé par la génération et par la CI

**Décision.** `pipeline/neutrality.py` porte le lexique et les règles. Il est
importé par `pipeline/check.py` (contrôle du contenu commité) et par
`pipeline/impacts.py` (annotation du brouillon). Source unique, jamais deux
copies. Il embarque une auto-vérification par `assert` sous `if __name__ ==
"__main__"`.

> **Amendé par DT-30 (§17).** L'auto-vérification par `assert` sous `__main__`
> est remplacée par une suite `unittest` sous `pipeline/tests/`. Le reste de la
> décision — module unique, importé par les deux appelants, jamais dupliqué —
> est inchangé.

**Justification.** DT-18 a déjà tranché ce motif pour `CHOICES`. Un lexique
dupliqué diverge, et la copie qui diverge est toujours celle de la CI.

**Conséquences.** `check.py` **échoue** sur une entrée malformée ou non neutre.
Il **avertit** sans échouer sur une couverture partielle ou absente. La
distinction est normative : *échouer sur ce qui est faux, avertir sur ce qui
manque*.

---

### DT-27 — Le vocabulaire de groupes est déclaré deux fois et vérifié

**Décision.** L'énumération vit dans `pipeline/check.py` (comme `THEMES`), les
libellés dans `web/src/lib/ui.js` (comme `THEMES[lang]`). Un test Node vérifie
que les clés de `GROUPS.fr` et `GROUPS.en` sont identiques et couvrent toutes
les valeurs présentes dans `content/impacts/`.

**Justification.** Reproduit exactement le dispositif existant pour les thèmes,
qui fonctionne. Un fichier de vocabulaire partagé Python/JS serait un mécanisme
nouveau pour un problème que le dépôt résout déjà.

---

### DT-28 — L'étape `impacts` reste hors de `--step all`

**Décision.** `pipeline/run.py` enregistre `impacts` dans `STEPS`, mais `all`
reste `["fetch", "extract"]`.

**Justification.** Identique au motif déjà écrit dans `run.py` pour `generate` :
l'appel de modèle coûte de l'argent et exige un relecteur, il est donc toujours
un choix explicite.

---

### DT-29 — Aucune abstraction de fournisseur ; un point d'appel unique

**Décision.** Aucune interface `Provider`, aucune couche d'adaptation. L'appel
au fournisseur est isolé dans une fonction unique de signature
`run_batch(requests) -> dict[str, dict]`, partagée par les deux passes. Chaque
entrée de contenu porte le champ `model`.

**Justification.** Une interface à implémentation unique coûte aujourd'hui plus
que la réécriture ne coûtera demain — et le dépôt rejette déjà explicitement
l'abstraction anticipée (« abstraction multi-pays avant le second pays »). Le
contrat réel avec le modèle tient en trois objets déjà constants dans
`generate.py` : le schéma de sortie, le texte du prompt, le fichier écrit.
Changer de fournisseur, c'est réécrire une quinzaine de lignes.

**Ce qui rend un changement de fournisseur sûr n'est pas un adaptateur, c'est le
linter en CI.** Un modèle local sera nettement plus faible sur la neutralité ; la
garantie ne peut pas reposer sur le prompt, elle doit reposer sur la
vérification du produit commité.

**Conséquences.** Un fournisseur sans API batch se branche derrière la même
signature par une boucle synchrone. Le champ `model` rend visible dans le diff
tout changement de modèle et trace une régénération partielle.

**Alternatives rejetées.** Protocole `Provider` + implémentation Anthropic :
rejeté, DT-01 et le principe d'économie du dépôt. Bibliothèque d'abstraction
tierce : rejetée, dépendance supplémentaire pour un besoin hypothétique.

> **Amendé par DT-31 (§17).** Le fournisseur et le modèle deviennent des valeurs
> de configuration, dans `pipeline/llm.py`. L'interdiction d'abstraction est
> maintenue et resserrée : un dictionnaire de fonctions, jamais un protocole.

---

## 5 — Schéma JSON final

### 5.1 Contenu : `content/impacts/<élection>.json`

```json
{
  "election": "fr-2027",
  "impacts": {
    "lr-depense-publique": {
      "of": "9f2c…64 caractères hexadécimaux…",
      "model": "claude-opus-5",
      "reviewed": "2026-08-14",
      "items": [
        {
          "kind": "implication",
          "basis": "text",
          "span": "réduisant la dépense publique plutôt qu'en augmentant toujours plus la pression fiscale",
          "fr": "La mesure porte l'ajustement budgétaire sur le niveau de dépense plutôt que sur le niveau de prélèvement.",
          "en": "The measure places budget adjustment on spending levels rather than on tax levels."
        },
        {
          "kind": "affected",
          "basis": "text",
          "who": "state_services",
          "directness": "direct",
          "span": "l'ordre dans nos comptes",
          "fr": "Les administrations de l'État sont visées par l'ajustement décrit.",
          "en": "State administrations are targeted by the described adjustment."
        },
        {
          "kind": "effect",
          "basis": "inferred",
          "fr": "Les arbitrages budgétaires annuels pourraient être révisés selon les modalités retenues.",
          "en": "Annual budget trade-offs could be revised depending on the arrangements chosen."
        }
      ]
    }
  }
}
```

### 5.2 Contraintes normatives

| Champ | Type | Contrainte |
|---|---|---|
| `election` | string | Égal au nom du fichier sans extension |
| `impacts` | object | Clés = `point.id` existants dans `content/programs/<élection>/` |
| `of` | string | `^[0-9a-f]{64}$` — SHA-256 de la citation normalisée |
| `model` | string | Identifiant du modèle ayant produit la passe 1 ; `"manual"` si écrit à la main |
| `reviewed` | string | `YYYY-MM-DD`, date de validation humaine |
| `items` | array | 3 à 10 éléments, ordre canonique (DT-25) |
| `items[].kind` | enum | `implication` \| `affected` \| `effect` |
| `items[].basis` | enum | `text` \| `inferred` |
| `items[].span` | string | Requis **ssi** `basis == "text"`. ≤ 300 caractères. Verbatim dans le document (INV-19) |
| `items[].who` | enum | Requis **ssi** `kind == "affected"`. Valeur du §6 |
| `items[].directness` | enum | Requis **ssi** `kind == "affected"`. `direct` \| `indirect` |
| `items[].fr` | string | Non vide, ≤ 200 caractères |
| `items[].en` | string | Non vide, ≤ 200 caractères |

**Aucune clé supplémentaire n'est admise, à aucun niveau.** Une clé inconnue
fait échouer la CI. C'est ce qui garantit qu'une annotation d'audit oubliée lors
du transfert depuis `review/` ne peut pas atteindre `content/`.

### 5.3 Brouillon : `review/<élection>-impacts-draft.json`

Même forme, plus deux champs d'annotation par énoncé, **absents du contenu
commité** :

```json
{
  "kind": "effect",
  "basis": "inferred",
  "fr": "…",
  "en": "…",
  "lint": ["fr: terme évaluatif « massif »"],
  "audit": { "verdict": "evaluative", "evidence": "massif" }
}
```

Le brouillon est groupé par point, la citation en tête, suivie du contexte
documentaire fourni au modèle. Il contient **tous** les énoncés produits, y
compris ceux signalés (DP-36).

### 5.4 Schéma de sortie du modèle — passe 1

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind":       { "type": "string", "enum": ["implication", "affected", "effect"] },
          "basis":      { "type": "string", "enum": ["text", "inferred"] },
          "span":       { "type": "string" },
          "who":        { "type": "string", "enum": ["…les 22 valeurs du §6…"] },
          "directness": { "type": "string", "enum": ["direct", "indirect"] },
          "fr":         { "type": "string" },
          "en":         { "type": "string" }
        },
        "required": ["kind", "basis", "fr", "en"],
        "additionalProperties": false
      }
    }
  },
  "required": ["items"],
  "additionalProperties": false
}
```

Les conditionnalités (`span` ssi `text`, `who`/`directness` ssi `affected`) ne
sont **pas** exprimées dans le schéma — elles le seraient au prix d'un
`oneOf` que les schémas stricts d'API n'acceptent pas uniformément. Elles sont
vérifiées par le linter, qui est de toute façon la couche opposable.

### 5.5 Schéma de sortie du modèle — passe 2

```json
{
  "type": "object",
  "properties": {
    "verdicts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "index":    { "type": "integer" },
          "verdict":  { "type": "string",
                        "enum": ["ok", "evaluative", "speculative", "unsupported",
                                 "overgeneral", "partisan", "offtopic"] },
          "evidence": { "type": "string" }
        },
        "required": ["index", "verdict", "evidence"],
        "additionalProperties": false
      }
    }
  },
  "required": ["verdicts"],
  "additionalProperties": false
}
```

---

## 6 — Vocabulaire fermé des groupes concernés

22 valeurs. Ajouter une valeur est une décision éditoriale documentée.

| `who` | fr | en |
|---|---|---|
| `associations` | Associations et organismes à but non lucratif | Nonprofits and associations |
| `businesses` | Entreprises | Businesses |
| `citizens` | Particuliers | Individuals |
| `departments` | Départements | Departments |
| `employees` | Salariés | Employees |
| `farmers` | Exploitations agricoles | Farms |
| `foreign_nationals` | Ressortissants étrangers | Foreign nationals |
| `healthcare` | Professionnels et établissements de santé | Healthcare providers |
| `judiciary` | Juridictions | Courts |
| `law_enforcement` | Forces de l'ordre | Law enforcement |
| `local_authorities` | Collectivités territoriales | Local authorities |
| `municipalities` | Communes | Municipalities |
| `owners` | Propriétaires | Owners |
| `public_bodies` | Organismes publics et opérateurs de l'État | Public bodies and state operators |
| `regions` | Régions | Regions |
| `retirees` | Retraités | Retirees |
| `schools` | Établissements d'enseignement | Educational institutions |
| `self_employed` | Indépendants et professions libérales | Self-employed and professionals |
| `state_services` | Services de l'État et ministères | State services and ministries |
| `students` | Élèves et étudiants | Students |
| `taxpayers` | Contribuables | Taxpayers |
| `tenants` | Locataires | Tenants |

**Règles d'emploi, normatives.**

- **Repli sur le niveau de collectivité.** Si le document ne précise pas le
  niveau, la valeur est `local_authorities`. `municipalities`, `departments` et
  `regions` ne s'emploient que lorsque le niveau est nommé dans le document. Sans
  cette règle, le modèle devine un échelon administratif.
- **`citizens` est libellé « Particuliers », pas « Citoyens ».** « Citoyen »
  exclut par construction les résidents étrangers ; le mot est en outre un
  marqueur rhétorique fréquent. « Particuliers » est le terme administratif
  neutre.
- **`foreign_nationals`** est le terme juridique neutre. Aucune autre
  désignation n'est admise pour ce groupe.
- **Un énoncé `affected` porte exactement un groupe.** Deux groupes concernés
  font deux énoncés.

---

## 7 — Invariants

### INV-19 — Une conséquence dite « prévue par le texte » est vérifiée mot pour mot

**Énoncé.** Tout énoncé `basis: "text"` porte un `span` qui apparaît verbatim,
après normalisation, dans le document déclaré par la source du point.

**Pourquoi.** C'est le seul mécanisme qui transforme la distinction fait /
inférence en propriété vérifiée plutôt qu'en affirmation. Sans lui, la
fonctionnalité entière repose sur la parole d'un modèle.

**Ce qui le protège.** `pipeline/check.py`, en réutilisant la mécanique de
`check_quotes` : `haystack()` sur le document, effondrement des blancs sur le
`span`, test d'inclusion. Hors ligne, la vérification est **rapportée comme
ignorée**, jamais silencieusement passée — comme aujourd'hui pour les citations.

**Comment il peut être cassé.** Rendre `span` facultatif « parce que le modèle
n'en trouve pas ». Normaliser le `span` plus agressivement que le document pour
faire passer un cas récalcitrant. Autoriser un `span` issu d'un autre document.

**Comment vérifier.** Le job `sources` de `daily.yml` exécute déjà `fetch` puis
`check` : la vérification tourne à chaque exécution.

---

### INV-20 — L'analyse n'atteint jamais le bundle du questionnaire

**Énoncé.** Aucune donnée de `content/impacts/` — texte, `span`, groupe — n'est
présente dans la page de questionnaire compilée ni dans les avoirs JavaScript
qu'elle référence.

**Pourquoi.** DP-30, et prolongement direct d'INV-01.

**Ce qui le protège.**
- **Structurel :** `content/impacts/` n'est importé que par `results.astro`.
- **Test :** `check-blindness.mjs` lit ses termes interdits depuis
  `content/programs/` et couvre déjà toute fuite d'identité de formation par ce
  chemin, sans modification.

**Comment il peut être cassé.** Importer les analyses dans un composant partagé
entre les deux pages — vecteur explicitement signalé par INV-01.

**Comment vérifier.** `npm run build && npm run check:blindness`. Et le critère
d'acceptation A-7 : le HTML compilé du questionnaire est **identique octet à
octet** avant et après la fonctionnalité.

---

### INV-21 — Aucun énoncé évaluatif dans le contenu commité

**Énoncé.** Aucun énoncé de `content/impacts/` ne contient de terme évaluatif,
de verbe de valeur, d'intensificateur, de superlatif, de généralisation non
soutenue ni d'affirmation au futur sur une inférence.

**Pourquoi.** C'est la contrainte de neutralité rendue opposable. Une consigne de
prompt n'est pas vérifiable ; une liste appliquée au contenu commité l'est.

**Ce qui le protège.** `pipeline/neutrality.py`, exécuté par `pipeline.check` en
CI. La garantie porte sur le contenu, pas sur le producteur : elle survit à un
changement de modèle ou de fournisseur (DT-29).

**Comment il peut être cassé.** Assouplir le lexique pour débloquer une
régénération. Appliquer le linter au seul brouillon et non au contenu.
Introduire une liste d'exceptions par entrée.

**Limite connue et à énoncer.** Le lexique est lui-même un artefact éditorial.
Il est court, en clair dans le dépôt, et modifié par le même processus de
relecture que le contenu. Il produit des faux positifs : la doctrine du dépôt est
qu'on reformule — *la vérification stricte vaut mieux que la vérification
intelligente* (précédent : le sigle « Ensemble »).

---

### INV-22 — Symétrie d'exposition

**Énoncé.** Les plafonds de DP-33 sont identiques pour toutes les formations, et
une question n'affiche d'analyse que si toutes ses positions en ont une (DP-34).

**Pourquoi.** Le volume et la présence sont des arguments. Une asymétrie dans
l'unité de comparaison est un biais que nulle phrase neutre ne compense.

**Ce qui le protège.** Les bornes en CI ; la règle tout-ou-rien appliquée au
rendu, au build, dans `results.astro`.

**Comment il peut être cassé.** Relever le plafond « pour une mesure
particulièrement dense ». Afficher partiellement « en attendant de compléter ».

**Comment vérifier.** Critère d'acceptation A-5.

---

### INV-23 — Rien de généré n'entre dans `content/` sans relecture humaine

**Énoncé.** Le pipeline n'écrit jamais dans `content/`. Il écrit dans `review/`,
qui est ignoré par git. Le transfert vers `content/` est un geste humain.

**Pourquoi.** C'est déjà la règle de fait pour les questions
(`generate.py` → `review/`). L'écrire comme invariant l'empêche d'être érodée
par une automatisation « qui fait gagner du temps ».

**Ce qui le protège.** Structurel : `impacts.py` ne connaît qu'un chemin
d'écriture, `ROOT / "review"`. Plus le champ `reviewed`, dont l'absence fait
échouer la CI.

**Comment il peut être cassé.** Une action CI qui ouvre une PR avec le contenu
généré — apparemment inoffensive puisqu'une PR se relit, en réalité une
relecture de diff volumineux au lieu d'une lecture d'énoncé.

**Comment vérifier.** `grep` sur les chemins d'écriture de `pipeline/impacts.py`.

---

## 8 — Rôles : LLM, linter, relecture humaine

| | **Passe 1 — génération** | **Passe 2 — audit** | **Linter** | **Relecture humaine** |
|---|---|---|---|---|
| Rôle | Propose | Signale | Interdit | Décide |
| Voit | Thème, citation, contexte documentaire, vocabulaire | Énoncés, citation, contexte | Énoncés seuls | Tout |
| Ne voit pas | **L'identité de la formation** (DP-35) | L'identité, **et le prompt de la passe 1** (DP-36) | — | — |
| Produit | `items` | Un verdict par énoncé | Une liste de violations | Le contenu commité |
| S'exécute | Hors ligne, à la demande | Hors ligne, à la demande | À la génération **et en CI** | Avant chaque commit |
| Peut écrire dans `content/` | Non | Non | Non | **Oui, seule** |
| Peut supprimer un énoncé | Non | **Non** (annote) | Non | Oui |

**Procédure de relecture, normative.**

1. `python -m pipeline.run --election fr-2027 --step impacts` écrit
   `review/fr-2027-impacts-draft.json`.
2. Le relecteur lit **point par point**, la citation en tête. Pour chaque
   énoncé : est-il descriptif ? Le `span` le soutient-il réellement ? Un énoncé
   `inferred` est-il bien conditionnel ?
3. Les annotations `lint` et `audit` orientent la lecture ; elles ne la
   remplacent pas. Un énoncé marqué `ok` peut être refusé.
4. Les énoncés retenus sont transférés dans `content/impacts/fr-2027.json`, sans
   les champs d'annotation, avec `reviewed` à la date du jour. Le relecteur peut
   réécrire un énoncé ou en ajouter un à la main ; `model` passe alors à
   `"manual"` si l'entrée entière est manuelle.
5. `python -m pipeline.check` doit passer avant le commit.
6. Une question dont toutes les positions ne sont pas couvertes n'affiche rien
   (DP-34) : c'est un état normal, pas un travail inachevé à masquer.

---

## 9 — Prompts normatifs

Les deux prompts ci-dessous sont **le texte à implémenter**, aux constantes de
vocabulaire près. Toute modification ultérieure est une décision documentée, car
elle invalide le contenu déjà relu.

### 9.1 Passe 1 — système

```
Tu décris les conséquences d'une mesure extraite d'un document officiel. Tu ne
sais pas de quelle formation politique elle provient, tu ne dois pas le deviner
et tu ne dois jamais l'évoquer.

Trois catégories d'énoncés :
- implication : ce que la mesure change mécaniquement — obligation, droit,
  restriction, procédure, règle fiscale ou réglementaire.
- affected : une catégorie de personnes ou d'organismes concernée, et en quoi.
  La catégorie est CHOISIE dans la liste fournie, jamais rédigée. Un énoncé
  porte exactement une catégorie. Si le document ne nomme pas le niveau de
  collectivité, emploie « local_authorities ».
- effect : un effet concret raisonnablement attendu.

Chaque énoncé porte un `basis` :
- "text"     : soutenu par le document. Tu fournis alors `span`, copié À
               L'IDENTIQUE depuis le contexte fourni, sans reformulation, sans
               coupure au milieu d'un mot, 300 caractères au plus.
- "inferred" : non écrit dans le document. Pas de `span`. Formulation
               obligatoirement conditionnelle.

Interdits absolus :
- terme évaluatif : bon, mauvais, juste, injuste, excellent, catastrophique,
  massif, historique, courageux, laxiste, généreux, indispensable, dérisoire,
  véritable, enfin ;
- verbe de valeur : aider, pénaliser, protéger, favoriser, défavoriser,
  sanctionner, nuire, récompenser, punir, améliorer, dégrader ;
- intensificateur : énormément, considérablement, dramatiquement, fortement,
  très, extrêmement, particulièrement ;
- jugement sur l'opportunité, l'efficacité, le coût politique ou le mérite ;
- chiffre absent du document ;
- scénario politique : élection, majorité, opposition, mandat, réaction ;
- superlatif, point d'exclamation ;
- « tous », « toutes », « aucun », « chaque », « toujours », « jamais »,
  « l'ensemble des » — sauf si le mot figure dans le span que tu fournis ;
- nom de parti, de personnalité, de mouvement, ou marqueur lexical de camp.

Un énoncé "inferred" emploie le conditionnel ou un marqueur d'incertitude
(« pourrait », « pourraient », « serait », « est susceptible de », « selon les
modalités retenues », « en fonction de »). Jamais le futur de l'indicatif.

Lorsque plusieurs effets sont plausibles, tu les énonces tous plutôt que d'en
choisir un.
Lorsque tu n'as pas de quoi produire un énoncé, tu n'en produis pas : un
tableau court est correct, un tableau inventé ne l'est pas.

Bornes, par mesure :
- 1 à 4 énoncés "implication", 1 à 5 énoncés "affected", 0 à 4 énoncés "effect" ;
- 10 énoncés au total au plus ;
- le nombre d'énoncés "inferred" ne dépasse jamais celui des énoncés "text" ;
- chaque énoncé fait 200 caractères au plus, en français comme en anglais, et
  les deux versions disent la même chose.

Rends du JSON conforme au schéma et rien d'autre.
```

**Message utilisateur.**

```
Thème : {theme}

Mesure :
« {quote} »

Contexte du document :
{context}

Catégories admises pour `who` :
{who_vocabulary}
```

`context` : fenêtre de ±1500 caractères autour de la citation dans le texte
normalisé du document, découpée sur des frontières de mots.
**Aucun titre de document, aucun nom de fichier, aucun identifiant de point n'y
figure** (DP-35).

### 9.2 Passe 2 — système

```
Tu vérifies des énoncés produits par un autre système. Tu ne les réécris pas,
tu les juges un par un. Tu ne connais pas les consignes suivies pour les
produire et tu ne dois pas les supposer.

Verdicts possibles :
- ok          : descriptif, soutenu, sans jugement
- evaluative  : jugement de valeur, verbe de valeur, terme connoté,
                intensificateur
- speculative : présenté comme certain sans être écrit dans le document, ou
                rédigé au futur de l'indicatif
- unsupported : basis "text", mais le span ne soutient pas l'énoncé
- overgeneral : généralisation ou quantification sans support textuel
- partisan    : marqueur de camp, parti, personnalité, mouvement
- offtopic    : ne découle pas de la mesure citée

`evidence` : le fragment exact de l'énoncé qui motive le verdict, ou "" si ok.

Dans le doute, tu signales. Un faux signalement coûte une lecture ; un
signalement manqué coûte la neutralité du produit.
```

**Message utilisateur.** La mesure, le contexte, et les énoncés numérotés à
partir de 0, chacun avec son `kind`, son `basis` et son `span` s'il en a un.

---

## 10 — Règles du linter déterministe

`pipeline/neutrality.py`. Le lexique ne s'applique **qu'aux champs `fr` et
`en`**, jamais à un `span` ni à une citation.

### 10.1 Échecs — la CI échoue

| # | Règle |
|---|---|
| L-01 | Clé inconnue, à n'importe quel niveau du fichier |
| L-02 | Identifiant de point inconnu, ou absent de `content/programs/` |
| L-03 | `of` ≠ SHA-256 de la citation normalisée du point |
| L-04 | `span` absent alors que `basis == "text"`, ou présent alors que `basis == "inferred"` |
| L-05 | `span` introuvable verbatim dans le document du point (ignoré et **rapporté** si le document n'est pas en cache) |
| L-06 | `who` ou `directness` présent sans `kind == "affected"`, ou absent avec |
| L-07 | `who` hors du vocabulaire du §6 |
| L-08 | Bornes de DP-33 non respectées (par `kind`, total, `inferred ≤ text`) |
| L-09 | Ordre des `items` non canonique (DT-25) |
| L-10 | `fr` ou `en` vide, ou > 200 caractères ; `span` > 300 caractères |
| L-11 | Identifiant, nom ou sigle de formation dans `fr` ou `en` (correspondance de mot entier, même mécanique que `check_questions`) |
| L-12 | Terme du lexique évaluatif, verbe de valeur ou intensificateur |
| L-13 | Superlatif (`le plus`, `la plus`, `le moins`, `the most`, `the least`) ou point d'exclamation |
| L-14 | Quantificateur non soutenu — `tous`, `toutes`, `aucun`, `aucune`, `chaque`, `toujours`, `jamais`, `l'ensemble des`, `la totalité`, `all`, `every`, `none`, `always`, `never` — **admis uniquement** si `basis == "text"` **et** si le même quantificateur figure dans le `span`. Conséquence en anglais : voir **R-9** |
| L-15 | `basis == "inferred"` sans marqueur d'incertitude |
| L-16 | `basis == "inferred"` avec une forme assertive de la liste fermée : `sera`, `seront`, `aura`, `auront`, `devra`, `devront`, `permettra`, `permettront`, `entraînera`, `entraîneront`, `augmentera`, `réduira`, `will `, `shall ` |
| L-17 | Chiffre (`\d`) dans un énoncé `inferred` ; ou dans un énoncé `text` sans figurer dans son `span` |
| L-18 | `reviewed` absent ou hors format `YYYY-MM-DD` |
| L-19 | Réécriture canonique différente du fichier lu, octet à octet (DT-25) |

### 10.2 Avertissements — la CI passe

| # | Règle |
|---|---|
| W-01 | Question dont certaines positions seulement ont une analyse (DP-34 : rien ne s'affiche) |
| W-02 | Point référencé par `positions.json` sans entrée d'analyse — **rapporté agrégé**, voir DT-32 |
| W-03 | Entrée dont `model` diffère du modèle courant du pipeline |
| W-04 | Vérification de `span` ignorée faute de documents en cache |

### 10.3 Lexiques

Listes de départ, en clair dans `neutrality.py`, une entrée par ligne, triées.
Elles s'étendent par relecture, jamais par exception ponctuelle.

**Français — évaluatif.** bon, bonne, mauvais, mauvaise, excellent, excellente,
remarquable, catastrophique, désastreux, juste, injuste, équitable, inéquitable,
ambitieux, courageux, historique, massif, massive, laxiste, ruineux, salutaire,
indispensable, urgent, nécessaire, insuffisant, dérisoire, généreux, scandaleux,
véritable, enfin.

**Français — verbes de valeur.** aider, pénaliser, protéger, favoriser,
défavoriser, sanctionner, nuire, récompenser, punir, améliorer, dégrader.

**Français — intensificateurs.** énormément, considérablement, dramatiquement,
fortement, très, extrêmement, particulièrement.

**Anglais — évaluatif.** good, bad, excellent, remarkable, catastrophic,
devastating, fair, unfair, ambitious, courageous, historic, massive, generous,
scandalous, essential, urgent, necessary, insufficient, negligible.

**Anglais — verbes de valeur.** help, harm, penalise, penalize, protect, favour,
favor, reward, punish, improve, worsen.

**Anglais — intensificateurs.** hugely, considerably, dramatically, greatly,
very, extremely, particularly, significantly.

**Marqueurs d'incertitude admis (L-15).** fr : pourrait, pourraient, serait,
seraient, susceptible, susceptibles, selon, en fonction de, peut, peuvent,
devrait, devraient. en : could, may, might, would, depending on, is expected to,
are expected to.

**Note d'implémentation.** `renforcer` et `réduire` ne figurent pas au lexique :
ce sont des verbes du document lui-même (ils sont dans le motif `COMMITMENT` de
`extract.py`) et leur interdiction rendrait la description impossible.
`améliorer` et `dégrader` y figurent : ils portent un jugement, pas une
description.

---

## 11 — Règles UX finales

### 11.1 Emplacement

Dans `results.astro`, à l'intérieur du `<li>` de chaque position, **après**
`<Source>`. La citation reste au-dessus et toujours visible : elle est la preuve
sur laquelle tout repose (INV-06), elle ne passe jamais sous l'analyse.

### 11.2 Structure

```
Les Républicains — soutient
  « citation verbatim »
  Document officiel · lien
  ▸ Ce que cette mesure implique          ← <details>, replié, sans attribut open
      Ce que le texte prévoit             ← <h3>
        · énoncé
          « fragment source »             ← <Quote>, lang="fr"
        Déduit du texte, non écrit dans le document.
        · énoncé conditionnel
      Qui est concerné                    ← <h3>
        · Communes — directement concernées
          énoncé
          « fragment source »
      Effets attendus                     ← <h3>
        Déduit du texte, non écrit dans le document.
        · énoncé conditionnel
```

### 11.3 Règles normatives

| # | Règle | Motif |
|---|---|---|
| U-01 | `<details>` natif, **replié par défaut**, jamais `open` | La preuve d'abord ; DT-01 (aucune dépendance) ; page lisible sans JS |
| U-02 | Trois sections au plus, groupées par `kind`, dans l'ordre `implication`, `affected`, `effect`. Une section vide n'est pas rendue | INV-14 : une absence n'est pas une section vide |
| U-03 | Titres de section en `<h3>` | La hiérarchie sous `#detail` s'arrête à `<h2>` ; `<h3>` est le niveau correct |
| U-04 | Dans une section, les énoncés `text` d'abord, les `inferred` ensuite | La preuve précède la déduction |
| U-05 | La phrase « Déduit du texte, non écrit dans le document. » apparaît **une fois par section**, avant le premier énoncé `inferred`, et seulement s'il y en a un | Une marque par énoncé serait le bruit qui cesse d'être lu (C6) |
| U-06 | **Aucun badge, aucune couleur, aucun pictogramme** pour distinguer `text` de `inferred` | INV-12, DP-22. La distinction est portée par la présence du fragment source |
| U-07 | Le `span` est rendu par `<Quote>` sans modification | DP-37 ; réutilise la serif de provenance, le filet et `lang="fr"` |
| U-08 | Un énoncé `affected` affiche `<strong>{libellé du groupe}</strong> — {directement \| indirectement} concerné(e)s`, puis l'énoncé | Le groupe est une donnée, pas une phrase |
| U-09 | Aucune animation | DP-21 |
| U-10 | Le bloc suit le sort de sa question : masqué si l'utilisateur n'a pas répondu | Comportement existant de `#detail`, inchangé |
| U-11 | La phrase de registres du bloc détail (`t.detailRegisters`) est **étendue à un quatrième registre** : nos reformulations, nos traductions, les citations, **nos déductions** | Système §3.7 et C6 : le registre est déclaré une fois pour le bloc qui les mélange. Sans cette extension, la page annonce trois registres et en affiche quatre |
| U-12 | Rien n'est rendu pour une question à couverture partielle | DP-34, INV-22 |
| U-13 | Zéro octet de JavaScript ajouté, zéro requête réseau ajoutée | DT-07 : tout est connu au build |

### 11.4 Libellés à créer dans `ui.js`

`impactSummary`, `impactImplications`, `impactAffected`, `impactEffects`,
`impactInferredNotice`, `impactDirect`, `impactIndirect`, et `GROUPS` (§6).
Sept chaînes plus le vocabulaire, dans les deux langues.

---

## 12 — Fichiers concernés

**Créés**

| Fichier | Rôle |
|---|---|
| `content/impacts/fr-2027.json` | Le contenu relu |
| `pipeline/impacts.py` | Deux passes batch, écriture dans `review/` |
| `pipeline/neutrality.py` | Lexique, règles L-01 à L-19, auto-vérification `assert` |
| `web/src/components/Impact.astro` | Le bloc replié |

**Modifiés**

| Fichier | Modification |
|---|---|
| `pipeline/check.py` | Chargement et validation de `content/impacts/`, appel du linter, avertissements W-01…W-04 |
| `pipeline/run.py` | Enregistrement de l'étape `impacts`, hors de `all` (DT-28) |
| `pipeline/extract.py` | Ajout d'un helper `context(text, quote, window)` |
| `web/src/pages/[lang]/results.astro` | Import, règle tout-ou-rien, rendu dans le `<li>` de position, extension de `detailRegisters` |
| `web/src/lib/ui.js` | `GROUPS` fr/en et sept libellés |
| `web/src/lib/ui.test.mjs` | Vérification de parité des clés `GROUPS` (DT-27) |
| `web/src/styles.css` | `details` imbriqué et liste d'énoncés — un bloc ajouté, pas de restructuration (DT-15) |
| `web/src/pages/[lang]/method.astro` | Statut épistémique (DP-38) |
| `content/README.md` | Quatrième famille de fichiers, garanties CI |
| `README.md` | Un paragraphe |

**Explicitement inchangés**

`api/` (DT-10) · `.github/workflows/daily.yml` — `pipeline.check` couvre déjà ·
`web/scripts/check-blindness.mjs` — couvre déjà toute fuite par ce chemin ·
`web/src/lib/score.js` · `web/src/pages/[lang]/index.astro` · `Question.astro` ·
`AnswerScale.astro`.

**Dépendances.** Aucune nouvelle dépendance npm (DT-01). Aucune nouvelle
dépendance Python : `hashlib` et `re` sont dans la bibliothèque standard,
`anthropic` est déjà présent.

---

## 13 — Critères d'acceptation

La fonctionnalité est acceptée quand **tous** les points suivants sont vérifiés.

### Contenu et CI

- **A-1** `python -m pipeline.check` passe sur un corpus comportant au moins une
  question entièrement couverte.
- **A-2** `python -m pipeline.check` **échoue**, avec un message nommant la règle,
  sur chacune des 19 violations L-01 à L-19, chacune couverte par un cas de test.
- **A-3** Les six exemples de la demande initiale servent de première fixture du
  linter : les trois exemples corrects passent ; les trois incorrects échouent,
  chacun sur la règle que le linter applique réellement.

  | Exemple | Règle | Motif |
  |---|---|---|
  | « aidera énormément » | **L-12** | « énormément » figure au lexique des intensificateurs |
  | « pénalisera » | **L-15** | déduction présentée comme un fait, sans marqueur d'incertitude |
  | « cette excellente réforme » | **L-12** | « excellente » figure au lexique évaluatif |

  > **Correction du 2 août 2026, à la livraison de PR-17.** La rédaction
  > initiale attribuait « pénalisera » à **L-16** et « cette excellente
  > réforme » à « L-13/L-12 ». Ni l'une ni l'autre n'était obtenable : L-16
  > porte une **liste fermée** de formes assertives qui ne contient pas
  > « pénalisera », et L-13 ne couvre que le superlatif et le point
  > d'exclamation. Le lexique apparie des **mots entiers** (mécanique de L-11),
  > donc « pénalisera » n'est pas apparié à « pénaliser » : c'est **L-15** qui
  > rejette l'énoncé, et c'est le comportement voulu — une déduction énoncée
  > comme un fait. **C'est la documentation qui est corrigée, jamais le
  > comportement.** Décision du responsable ; ni la liste fermée de L-16 ni la
  > portée de L-13 ne sont ouvertes.
- **A-4** ~~`pipeline/neutrality.py` exécuté directement passe son
  auto-vérification.~~ **Amendé par DT-30 :** `python -m unittest discover`
  passe, et la suite couvre `neutrality.py` règle par règle.
- **A-5** Une question dont une seule position porte une analyse n'affiche
  **aucune** analyse, et `check` émet W-01 sans échouer.
- **A-6** Hors ligne, la vérification des `span` est **rapportée comme ignorée**,
  jamais silencieusement passée, et `check` sort avec le code 0.
- **A-19** *(ajouté par DT-32)* `python -m pipeline.check` **échoue**, avec un
  message nommant la cause, lorsque `election` ne vaut pas le nom du fichier
  d'analyses, et lorsque le fichier d'analyses attendu pour un scrutin est
  absent. Ces deux contrôles sont des garanties, pas des détails
  d'implémentation.

### Cécité et neutralité

- **A-7** Le HTML compilé des pages `<lang>/index.html` est **identique octet à
  octet** avant et après la fonctionnalité. C'est le protocole de DT-20 appliqué
  ici, et c'est la preuve d'INV-20 la plus forte disponible.
- **A-8** `npm run build && npm run check:blindness` passe.
- **A-9** Aucun nom, sigle, identifiant de formation, ni titre de document ne
  figure dans le corps d'une requête envoyée au modèle (DP-35). Vérifié par un
  test sur la sortie de `build_requests`.

### Interface

- **A-10** La page de résultats est complète et navigable **JavaScript
  désactivé** : les blocs d'analyse s'ouvrent et se ferment.
- **A-11** Aucun octet de JavaScript ajouté à `results.astro` ; aucune requête
  réseau ajoutée.
- **A-12** Les tests de jetons et de contraste existants passent sans
  modification — la fonctionnalité n'introduit aucune couleur (INV-12).
- **A-13** L'ordre de tabulation reste l'ordre visuel dans un bloc ouvert
  (INV-17).
- **A-14** La phrase de registres annonce quatre registres (U-11).

### Pipeline

- **A-15** Une deuxième exécution de l'étape `impacts` sans changement de contenu
  ne produit **aucune** requête (régénération incrémentale, DT-24).
- **A-16** `--step all` n'exécute pas `impacts` (DT-28).
- **A-17** `impacts.py` n'a aucun chemin d'écriture hors de `review/` (INV-23).
- **A-18** Une réécriture canonique du fichier de contenu est identique au
  fichier commité (DT-25).

---

## 14 — Non-objectifs

Normatif (DP-39). Chacun de ces points est **refusé sans réexamen**.

**Jugement et notation**

1. Noter, classer ou scorer une mesure sur quelque échelle que ce soit.
2. Qualifier une mesure de bonne, mauvaise, efficace, inefficace, réaliste,
   irréaliste, ambitieuse ou timide.
3. Comparer deux mesures entre elles à l'intérieur d'un énoncé.
4. Signaler qu'une mesure est « soutenue par les économistes », « contestée »,
   « consensuelle ».

**Analyse économique et juridique**

5. Chiffrer le coût, le rendement ou l'impact budgétaire d'une mesure.
6. Produire une prévision macroéconomique, un effet sur l'emploi, sur la
   croissance ou sur les prix.
7. Évaluer la constitutionnalité, la compatibilité européenne ou la faisabilité
   juridique.
8. Estimer un délai de mise en œuvre.

**Fact-checking et contexte politique**

9. Vérifier si une promesse est tenable, cohérente avec une autre, ou déjà tenue.
10. Rapprocher une mesure d'un bilan, d'un mandat, d'une déclaration ou d'un
    vote passé.
11. Mentionner une élection, une majorité, une opposition, une personnalité ou
    un mouvement.
12. Décrire un effet de second tour, un scénario en chaîne ou une réaction
    politique attendue.

**Sources et autorité**

13. Citer une source tierce : presse, institut, rapport, expert, réseau social.
14. Ajouter une source qui ne soit pas le document officiel du point.

**Produit**

15. Afficher quoi que ce soit de l'analyse **pendant** le questionnaire (DP-30).
16. **Personnaliser l'analyse selon les réponses de l'utilisateur** — « ce que
    cela signifie pour vous ». Ce serait un profilage, et il violerait INV-03 et
    INV-04 sur la page même qui les revendique.
17. Générer une analyse au moment de la requête. Le site reste statique.
18. Exposer les analyses par une API publique.
19. Étendre au-delà de `fr`/`en`, ou traduire par une passe distincte de la
    génération (les deux langues sont produites ensemble pour ne pas diverger).
20. Produire une analyse pour un point non référencé par `positions.json`.
21. Résumer, tronquer ou reformuler une citation pour la faire tenir dans le
    bloc. Une citation raccourcie est une citation altérée (INV-06).

---

## 15 — Risques résiduels assumés

| # | Risque | Atténuation | Statut |
|---|---|---|---|
| R-1 | Le produit passe de « citer » à « expliquer » : la neutralité vérifiée par machine ne couvre plus 100 % de l'affiché. Les énoncés `inferred` ne seront jamais vérifiables | Marque structurelle par la preuve (DP-31), plafond `inferred ≤ text` (DP-33), déclaration en méthodologie (DP-38) | **Borné, non supprimé.** C'est le coût de la fonctionnalité |
| R-2 | Asymétrie de richesse entre formations | Plafonds identiques + tout-ou-rien (INV-22) | Traité |
| R-3 | Un LLM qui audite un LLM partage ses angles morts | Le linter en CI est la couche indépendante ; la passe 2 ne voit pas le prompt de la passe 1 ; un modèle différent est possible en passe 2 sans changement d'architecture | Traité |
| R-4 | Le lexique est un artefact éditorial | Court, en clair, relu comme du contenu, faux positifs assumés par reformulation | Déclaré (INV-21) |
| R-5 | Charge de relecture humaine — le coût dominant | Relecture par point, seulement sur les points périmés, brouillon groupé avec la citation en tête | **Assumé.** C'est le prix de INV-23 |
| R-6 | Une mesure trop vague empêche d'atteindre le plancher, et prive toute la question d'analyse | La relecture humaine peut écrire l'entrée à la main | Traité |
| R-7 | Le linter anglais est plus faible que le français | Les deux langues sont produites ensemble ; l'audit lit les deux | Déclaré |
| R-8 | Le fichier `docs/impacts/DECISION.md` n'est pas suivi par git : `.gitignore` ignore `*.md` | À la discrétion du responsable — une exception `!docs/**/*.md` le rendrait versionnable | À trancher hors DP |
| R-9 | **L-14 est structurellement plus strict en anglais qu'en français.** Les `span` sont français : un quantificateur anglais ne peut jamais être retrouvé dans un `span`, donc jamais soutenu. « Toutes les collectivités… » passe si le `span` porte « toutes » ; « All authorities… » échoue dans le même énoncé, alors que les deux versions doivent dire la même chose | Aucune correction de comportement. Un énoncé dont la version française porte un quantificateur soutenu se reformule **sans quantificateur en anglais**, ou la paire est revue à la relecture. La règle reste appliquée à la lettre : elle refuse une affirmation de couverture que le `span` ne porte pas, ce qui est son objet | **Déclaré à la livraison de PR-17, comportement inchangé.** Aucun contenu ne le rencontre tant que PR-20 n'écrit pas de quantificateur |

---

## 16 — Matrice décision → invariant → vérification

| Décision | Invariant | Vérifié par | Critère |
|---|---|---|---|
| DP-29 | INV-19 | `pipeline.check` (`span` verbatim) | A-1, A-2, A-6 |
| DP-30 | INV-20 | `check-blindness.mjs`, HTML identique | A-7, A-8 |
| DP-31 | INV-19, INV-21 | `pipeline.check`, linter L-04/L-05 | A-2 |
| DP-32 | INV-21 | L-07 + parité des clés `GROUPS` | A-2 |
| DP-33 | INV-22 | L-08 | A-2 |
| DP-34 | INV-22 | Rendu au build + W-01 | A-5 |
| DP-35 | INV-20 | Test sur `build_requests` | A-9 |
| DP-36 | INV-23 | Chemins d'écriture, champ `reviewed` | A-17, L-18 |
| DP-37 | INV-06 | `<Quote>` réutilisé sans modification | A-10 |
| DP-38 | — | Relecture de la page méthodologie | A-14 |
| DP-39 | — | Ce document | §14 |
| DT-25 | — | Réécriture canonique | A-18 |
| DT-29 | INV-21 | Le linter porte la garantie, pas le prompt | A-2 |

---

## 17 — Amendements postérieurs à l'approbation

**Statut.** Ces trois décisions ont été arrêtées le **2 août 2026**, entre
l'approbation de la DP et l'ouverture de la première PR, pour clore les trois
points que le découpage avait laissés ouverts (`ROADMAP.md`, ancienne §5). Elles
sont normatives au même titre que celles du corps du document et ne se
réinterprètent pas davantage.

---

### DP-40 — Corpus pilote avant génération complète

**Décision.** Les analyses sont produites en **deux temps**. D'abord un **corpus
pilote** : deux questions entièrement couvertes au sens de DP-34, choisies pour
maximiser la diversité — une question portant des positions de trois formations,
une question mono-formation — soit environ quatre points. La génération du reste
du corpus n'est ouverte qu'ensuite, et seulement si les conditions de stabilité
ci-dessous sont réunies.

**Contexte.** DT-24 dimensionnait un premier passage à 120 points. Rien n'oblige
à ce que le premier passage soit complet, et tout invite au contraire à ce qu'il
ne le soit pas.

**Justification.** Le coût dominant de la fonctionnalité est la relecture humaine
(R-5), et c'est aussi le seul filtre dont la qualité ne se mesure pas avant de
l'avoir exercé. Un pilote de quatre points fait tourner la chaîne entière —
génération aveugle, audit, linter, CI, relecture, forme canonique — pour une
charge de relecture d'une heure plutôt que d'une semaine. Ce qu'il révèle est
précisément ce qu'aucune conception ne pouvait prévoir : le taux de rejet réel,
le taux de faux positifs du lexique, l'ergonomie du brouillon. Générer 120 points
avant de savoir cela, c'est produire au prix fort une matière qu'il faudra
peut-être jeter — un prompt corrigé après coup invalide tout le contenu déjà relu
(§9).

**Conditions de stabilité, à vérifier avant la génération complète.**

1. Aucun lexique de `neutrality.py` n'a été raccourci depuis sa livraison, et
   aucune exception par entrée n'a été introduite (INV-21).
2. Aucun prompt de `impacts.py` n'a été modifié depuis le pilote — sinon le
   contenu déjà relu est invalidé et le pilote est à refaire.
3. Le taux de rejet en relecture du pilote est mesuré et consigné, et jugé
   acceptable par le responsable.
4. A-15 est vérifié en conditions réelles : une seconde exécution sur le pilote
   ne produit aucune requête.

**Conséquences.** La génération complète est livrée **par vagues de questions**,
jamais en une PR. Chaque vague est une PR de contenu autonome. Entre le pilote et
la première vague, le produit affiche des analyses sur deux questions et rien sur
les vingt-huit autres : c'est l'état normal décrit par DP-34, pas un travail
inachevé à masquer.

**Alternatives rejetées.** Génération complète immédiate : rejetée ci-dessus.
Pilote d'une seule question : rejeté, une question mono-formation ne teste pas la
règle du tout-ou-rien, qui est le mécanisme le plus susceptible d'être mal
implémenté.

---

### DT-30 — Suite de tests Python `unittest`, sous `pipeline/tests/`

**Décision.** Le dépôt se dote d'une **vraie suite de tests Python**, écrite avec
`unittest` de la bibliothèque standard, découverte par `python -m unittest
discover`, exécutée par la commande `checks` et par les deux workflows. Les
vérifications par `assert` sous `if __name__ == "__main__"` ne sont plus le
mécanisme de test du pipeline.

**Contexte.** Le dépôt n'avait aucun test Python : `check.py` est lui-même le
contrôle, et DT-26 prescrivait une auto-vérification par `assert` pour
`neutrality.py`. Les critères A-2 et A-3 exigent dix-neuf cas de test sur des
règles dont la moitié porte sur un fichier et un corpus, pas sur une chaîne.

**Justification.** Une auto-vérification sous `__main__` ne s'exécute que si
quelqu'un lance le module ; elle n'a ni découverte, ni rapport, ni assertion
lisible en échec, et elle ne peut pas porter de fixture de fichier. À dix-neuf
règles, elle devient un bloc d'`assert` que personne ne lit. `unittest` est dans
la bibliothèque standard — la décision **n'ajoute aucune dépendance** et reste
donc conforme à l'économie du dépôt (DT-01, §19 de `MIGRATION.md`).

**Conséquences.**
- `pipeline/tests/` est un paquet ; les tests importent le pipeline en relatif
  depuis la racine du dépôt.
- La commande `checks` de `CLAUDE.md` s'allonge d'une commande.
- `daily.yml` (job `checks`) et `pages.yml` exécutent la suite.
- L'auto-vérification `assert` de DT-26 est retirée de la conception : elle n'est
  pas écrite puis supprimée, elle n'est jamais écrite.
- Le critère A-4 est reformulé en conséquence (§13).

**Alternatives rejetées.** `pytest` : dépendance supplémentaire pour un gain nul
sur dix-neuf cas de test sans fixture complexe. Maintenir les `assert` sous
`__main__` : rejeté ci-dessus, et rejeté explicitement par le responsable.

---

### DT-31 — Fournisseur et modèle sont des valeurs de configuration

**Décision.** Le fournisseur et l'identifiant du modèle vivent dans
**`pipeline/llm.py`**, sous forme de deux constantes surchargeables par
l'environnement, à côté d'un **dictionnaire de fonctions** `PROVIDERS` et de la
fonction unique `run_batch(requests) -> dict[str, dict]` prescrite par DT-29. Le
fournisseur retenu est **Gemini**, appelé par **HTTP direct avec `requests`**,
déjà présent dans `requirements.txt`.

**Contexte.** DT-29 interdisait l'abstraction de fournisseur et isolait l'appel
dans une fonction unique, mais laissait le modèle en constante de module, comme
`generate.MODEL`. Le fournisseur effectivement retenu n'est pas celui que la DP
supposait.

**Justification.** Un dictionnaire de deux entrées possibles n'est pas une
abstraction : il n'y a ni interface, ni classe, ni inversion de dépendance, et un
fournisseur supplémentaire coûte une fonction et une ligne. Le passage par
`requests` plutôt que par un SDK conserve `requirements.txt` inchangé, donc
l'affirmation du §12 reste vraie. Et **ce qui rend un changement de fournisseur
sûr reste le linter en CI**, non le point d'appel : DT-29 est confirmé sur ce
point, pas contourné.

**Conséquences.**
- `pipeline/llm.py` fait autorité pour **W-03** : le « modèle courant du
  pipeline » est `llm.MODEL`. Ce point, laissé ouvert par la DP, est clos.
- Le champ `model` de chaque entrée de contenu porte la valeur effectivement
  employée, ce qui rend visible dans le diff toute régénération partielle.
- **`generate.py` n'est pas migré vers `llm.py`.** Il continue d'appeler
  Anthropic pour les questions. Le migrer serait un changement sans rapport avec
  l'objet d'une PR de cette feuille de route.
- La gestion des réponses 429 et 5xx est écrite à la main, une fois, dans
  `llm.py`. C'est le coût assumé de l'absence de SDK.
- L'API batch n'est pas employée pour le pilote : DT-29 admet explicitement la
  boucle synchrone derrière la même signature, et quatre points ne justifient
  pas davantage.

**Alternatives rejetées.** SDK `google-genai` : une quatrième dépendance Python,
et l'affirmation « aucune nouvelle dépendance » du §12 aurait cessé d'être vraie.
Protocole `Provider` : déjà rejeté par DT-29, et rien ici ne le rouvre. Modèle en
dur dans `impacts.py` : rejeté, c'est exactement ce que cet amendement corrige.

---

---

### DT-32 — Rapport agrégé de W-02, et deux contrôles de schéma rendus opposables

**Statut.** Arrêtée le 2 août 2026, à la validation de PR-16, à partir de ce que
l'implémentation a rencontré. Elle précise le §10 et le §13 ; elle ne change
aucune règle.

---

**1. W-02 est rapporté agrégé, non point par point.**

**Décision.** L'avertissement W-02 est émis **une fois**, portant le **nombre**
de points référencés par `positions.json` sans entrée d'analyse. L'énumération
des identifiants n'est pas produite.

**Pourquoi l'implémentation diffère de la formulation initiale.** Le §10.2
définit W-02 comme portant sur un point, ce qui se lit naturellement comme une
ligne par point. Sur le corpus réel, cela produit **48 lignes d'avertissement à
chaque exécution de la CI**, dans l'état normal du dépôt — un état qui durera
jusqu'à la fin de PR-23. Un avertissement qui se répète par dizaines à chaque
exécution cesse d'être lu, et c'est précisément W-01, qui est rare et
actionnable, qui se retrouverait noyé. La doctrine du §10 est *échouer sur ce qui
est faux, avertir sur ce qui manque* : elle suppose qu'un avertissement soit
encore un signal.

**Ce que la décision préserve.** Le décompte est exact et l'information n'est pas
perdue : la liste des points sans analyse se reconstitue exactement par
différence entre `positions.json` et `content/impacts/`, sans nous croire sur
parole. Ce qui est retiré est la répétition, pas la donnée.

**Ce qu'elle n'autorise pas.** W-01 reste **une ligne par question** : il est
rare, il désigne une question précise, et il annonce que du contenu relu ne
s'affichera pas. L'agrégation ne s'étend pas à lui.

**Alternative rejetée.** Énumérer les identifiants sous un seuil (par exemple dix
points) : le seuil aurait été une préférence, et le comportement aurait changé
silencieusement au franchissement de ce seuil.

---

**2. `election` doit valoir le nom du fichier — contrôle opposable.**

**Décision.** `pipeline.check` échoue si le champ `election` du fichier
d'analyses ne vaut pas le nom du fichier sans extension.

**Justification.** Le §5.2 l'exige déjà dans le tableau des contraintes, sans
qu'aucune règle L ne le porte. Un fichier `fr-2032.json` déclarant
`"election": "fr-2027"` passerait donc tous les contrôles tout en attestant le
mauvais scrutin. Le contrôle existait dans l'implémentation de PR-16 ; il est ici
énoncé comme garantie plutôt que laissé au hasard d'une relecture de code.

---

**3. Un fichier d'analyses absent est une erreur nommée, jamais un traceback.**

**Décision.** Si `content/impacts/<élection>.json` n'existe pas, `pipeline.check`
échoue avec un message le nommant, et non par une exception non rattrapée.

**Justification.** L'absence du fichier est un **état du contenu**, pas une panne
d'outil : le §5.1 en fait une des quatre familles de fichiers du dépôt. Une
exception non rattrapée en CI n'indique ni ce qui manque ni quoi faire, et se lit
comme un bug du pipeline plutôt que comme un défaut de contenu. C'est la même
doctrine que P8 côté produit : une absence s'affiche comme absence.

**Ce que la décision ne fait pas.** Elle n'introduit **aucun état intermédiaire**
— un fichier absent n'est pas traité comme un fichier vide. Un fichier vide est
un état légitime et déclaré ; un fichier manquant est une erreur.

---

**Numérotation.** Ces trois contrôles ne reçoivent **pas** de numéro dans la
série L : celle-ci reste identique aux dix-neuf règles du §10.1, afin que les
tests, les messages et le document continuent de se répondre un pour un. Les
deux contrôles de schéma sont couverts par le critère **A-19**.

---

**Fin de la DP.** Aucune décision de conception ne reste à prendre.
Le découpage en PR est figé dans `docs/impacts/ROADMAP.md`.
