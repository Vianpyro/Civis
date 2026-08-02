# Civis — Découpage en PR : conséquences concrètes d'une mesure

**Objet.** Plan d'implémentation de `docs/impacts/DECISION.md`. Sept PR,
numérotées **PR-15 à PR-21** : la numérotation prolonge celle du chantier
d'interface (PR-01 à PR-14, livré), comme DP-29 et DT-21 prolongent le registre
de décisions.

**Statut.** Ce document ne prend **aucune décision de conception**. Toute
question rencontrée pendant le découpage et non tranchée par la DP est reportée
au §5 plutôt que résolue ici — c'est la règle d'usage de la DP.

**Règle de découpage appliquée.** Celle du chantier précédent, qui a marché :
le garde-fou avant le contenu, le schéma avant les producteurs, le rendu séparé
de la matière, un point de conflit sérialisé explicitement.

---

## 1 — Vue d'ensemble

| PR | Objet | Volume estimé | Dépend de |
|---|---|---|---|
| **PR-15** | Schéma, fichier vide, validation structurelle en CI | ~350 | — |
| **PR-16** | `neutrality.py` : lexique et règles lexicales | ~400 | 15 |
| **PR-17** | Rendu : `Impact.astro`, tout-ou-rien, libellés | ~320 | 15 |
| **PR-18** | `impacts.py` passe 1, étape `impacts`, helper `context()` | ~300 | 15 |
| **PR-19** | Passe 2, annotations, régénération incrémentale | ~250 | 16, 18 |
| **PR-20** | Première vague de contenu relu | ~200–400 (JSON) | 15, 16, 17 |
| **PR-21** | Statut épistémique en méthodologie et documentation | ~150 | — |

```
PR-15 ─┬→ PR-16 ─┬→ PR-19
       ├→ PR-18 ─┘
       ├→ PR-17 ──→ PR-20
PR-21 ─── indépendante de tout
```

**Parallélisable :** 17 ∥ 18 ∥ 21 dès PR-15 fusionnée. **Jamais simultanées :**
15 et 16 (même fichier, voir §4).

**Ce que chaque PR laisse derrière elle.** Après PR-15, le dépôt valide un
fichier d'analyses vide. Après PR-17, il sait en afficher, et n'en affiche
aucune. Après PR-19, il sait en produire des brouillons. Après PR-20, la
fonctionnalité est visible. Aucune de ces étapes n'est un état intermédiaire
incohérent : un corpus sans analyse est l'état normal décrit par DP-34.

---

## 2 — Les sept PR

### PR-15 — Schéma d'analyses, fichier vide, validation structurelle

**Objectif.** Faire exister `content/impacts/fr-2027.json`, le charger en CI et
le valider sur tout ce qui ne demande pas de lexique : forme, bornes, ordre
canonique, cohérence avec `programs/` et `positions.json`. Aucune interface,
aucun contenu, aucun appel de modèle.

**Fichiers modifiés**
- `pipeline/check.py` — chargement de `content/impacts/`, règles **L-01 à L-10**,
  **L-18**, **L-19**, avertissements **W-01 à W-04**, énumération `GROUPS`
  (22 valeurs, DT-27) à côté de `THEMES`.
- `content/README.md` — quatrième famille de fichiers, schéma, garanties CI.

**Nouveaux fichiers**
- `content/impacts/fr-2027.json` — `{"election": "fr-2027", "impacts": {}}`.
  Un fichier vide est nécessaire dès cette PR : `results.astro` l'importera en
  PR-17 et un import manquant casse le build. C'est une conséquence du
  découpage, pas une décision : DP-34 rend `impacts: {}` sémantiquement correct.
- Les cas de test de A-2 — **emplacement à trancher, voir §5.1**.

**Dépendances.** Aucune. Peut être ouverte immédiatement.

**Risques**
- `pipeline/check.py` est le point de conflit unique côté pipeline, exactement
  ce que `styles.css` était côté web. **PR-15 et PR-16 ne peuvent pas être
  ouvertes simultanément** : PR-16 y insère l'appel du linter dans le code que
  PR-15 vient d'écrire.
- Un chargement trop strict casse la CI existante sur un dépôt sans analyses.
  Atténuation : le fichier vide est livré dans la même PR, et W-02 avertit sans
  échouer sur les 120 points sans entrée.
- L'énumération `GROUPS` est écrite ici et ses libellés en PR-17 : deux
  déclarations séparées par une PR. C'est le dispositif voulu (DT-27), mais le
  test de couverture qui les rapproche n'existe qu'à partir de PR-17.

**Tests à ajouter**
- Un cas par règle portée : **L-01 à L-10, L-18, L-19**, chacun échouant avec un
  message nommant la règle.
- Réécriture canonique : un fichier correct se resérialise à l'identique
  (**A-18**) ; un fichier aux clés non triées ou aux `items` désordonnés échoue.
- `of` : le condensé attendu est celui de la citation normalisée par
  `haystack()`, calculé dans le test à partir du corpus réel.
- Couverture partielle : une question dont une seule position porte une entrée
  produit **W-01** et un code de sortie 0.
- Hors ligne : la vérification des `span` est **rapportée ignorée**, jamais
  passée en silence (**A-6**).

**Critères d'acceptation**
1. `python -m pipeline.check` passe sur le dépôt tel que livré (analyses vides),
   et affiche les avertissements W-02 sans échouer.
2. Chacune des douze règles portées échoue avec un message la nommant (**A-2**,
   part de PR-15).
3. **A-18** vérifié : réécriture canonique identique octet à octet.
4. **A-6** vérifié.
5. `--step all` inchangé ; aucun fichier de `web/` modifié ; sortie compilée
   identique octet à octet.
6. Aucune dépendance Python ajoutée.

---

### PR-16 — `pipeline/neutrality.py` : lexique et règles lexicales

**Objectif.** Rendre la neutralité opposable sur le contenu commité : le module
unique de DT-26, ses six lexiques, les règles qui portent sur les champs `fr` et
`en`, et son auto-vérification.

**Fichiers modifiés**
- `pipeline/check.py` — import et appel de `neutrality`, sur les seuls champs
  `fr`/`en` (jamais un `span`, jamais une citation).

**Nouveaux fichiers**
- `pipeline/neutrality.py` — lexiques du §10.3 en clair, une entrée par ligne,
  triées ; règles **L-11 à L-17** ; auto-vérification par `assert` sous
  `if __name__ == "__main__"`.

**Dépendances.** PR-15 (même fichier `check.py`, et les règles lexicales
s'appliquent à des entrées déjà validées structurellement).

**Risques**
- **Faux positifs** (R-4). La doctrine est de reformuler, pas d'assouplir. Le
  risque réel n'est pas le faux positif : c'est la liste d'exceptions par entrée
  qui naîtra du premier blocage. Elle est interdite (INV-21) et doit être
  refusée en revue.
- L-14 (quantificateurs admis si présents dans le `span`) et L-17 (chiffres) sont
  les deux règles à état : elles lisent l'énoncé **et** son `span`. Ce sont
  celles où une erreur passe inaperçue, parce qu'elles échouent en laissant
  passer plutôt qu'en bloquant.
- Le lexique anglais est plus faible que le français (R-7) : déclaré, non traité.

**Tests à ajouter**
- Un cas par règle : **L-11 à L-17**, avec le fragment fautif dans le message.
- **A-3** : les six exemples de la demande initiale servent de première fixture —
  les trois corrects passent, « aidera énormément » échoue en L-12 et L-16,
  « pénalisera » en L-12 et L-16, « cette excellente réforme » en L-12 et L-13.
- L-14 : le même quantificateur admis avec `basis: "text"` et un `span` qui le
  contient, refusé sans lui et refusé sur `inferred`.
- L-15/L-16 : un énoncé `inferred` au futur de l'indicatif échoue ; le même au
  conditionnel passe.
- Auto-vérification : `python -m pipeline.neutrality` sort 0 (**A-4**).

**Critères d'acceptation**
1. **A-2** complet : les 19 règles L-01 à L-19 échouent chacune avec son nom.
2. **A-3** et **A-4** vérifiés.
3. Le lexique n'est appliqué à aucun `span` ni à aucune citation — vérifié par un
   cas où un terme évaluatif figure dans un `span` et où `check` passe.
4. Aucune liste d'exceptions par entrée, à aucun endroit du module.
5. Une seule déclaration du lexique dans le dépôt.

---

### PR-17 — Rendu : `Impact.astro`, tout-ou-rien, libellés et vocabulaire

**Objectif.** Afficher une analyse quand elle existe, et rien du tout quand la
question n'est pas entièrement couverte. Zéro octet de JavaScript ajouté.

**Fichiers modifiés**
- `web/src/pages/[lang]/results.astro` — import de `content/impacts/`, règle
  tout-ou-rien au build, rendu dans le `<li>` de position **après** `<Source>`,
  extension de `t.detailRegisters` au quatrième registre (U-11).
- `web/src/lib/ui.js` — `GROUPS` fr/en (22 valeurs) et les sept libellés du §11.4.
- `web/src/lib/ui.test.mjs` — `GROUPS` entre dans `TABLES` ; test de couverture
  des valeurs `who` réellement employées (DT-27).
- `web/src/styles.css` — un bloc **ajouté en fin de fichier** : `details` imbriqué
  et liste d'énoncés. Aucune restructuration (DT-15).

**Nouveaux fichiers**
- `web/src/components/Impact.astro` — le bloc replié, U-01 à U-09.

**Dépendances.** PR-15 (le fichier importé doit exister).

**Risques**
- **INV-20.** Le vecteur nommé par la DP est l'import des analyses dans un
  composant partagé entre les deux pages. `Impact.astro` doit être importé par
  `results.astro` et par rien d'autre, au même titre que `Quote` et `Source`.
- **`<details>` imbriqué dans `<details>`.** Le bloc d'analyse s'ouvre à
  l'intérieur du `<details>` de question déjà rendu par `results.astro`. Le
  comportement natif est correct, mais c'est le point où l'ordre de tabulation
  peut se dissocier de l'ordre visuel (**A-13**, INV-17). Vérification **M1**.
- Le volume HTML de la page de résultats croît. Assumé, comme en PR-10 : la
  contrepartie est zéro requête et zéro script (A-11).
- Le regroupement par `kind` est une opération de rendu (DT-22) : une section
  vide ne doit pas être rendue, pas même comme titre (U-02, INV-14).

**Tests à ajouter**
- Parité des clés `GROUPS.fr` / `GROUPS.en` — obtenue par ajout à `TABLES`, les
  trois tests génériques existants s'appliquent alors sans ligne nouvelle.
- Couverture : toute valeur `who` présente dans `content/impacts/` possède un
  libellé dans les deux langues (DT-27).
- Les tests de jetons et de contraste existants passent **sans modification**
  (**A-12**) : la fonctionnalité n'introduit ni couleur ni valeur hors échelle.

**Critères d'acceptation**
1. **A-7** : le HTML compilé de `<lang>/index.html` est identique octet à octet
   avant et après. Protocole DT-20.
2. Tant que `impacts` est vide, le HTML compilé de `<lang>/results.html` est lui
   aussi identique octet à octet — la PR n'affiche rien avant qu'il y ait
   quelque chose à afficher.
3. **A-8**, **A-10** (page navigable JavaScript désactivé, blocs ouvrables),
   **A-11** (zéro octet de JS ajouté, zéro requête), **A-12**, **A-13**,
   **A-14** (la phrase de registres en annonce quatre).
4. U-01 à U-09 vérifiés par lecture : `<details>` replié sans `open`, aucun badge,
   aucune couleur, aucun pictogramme, `<Quote>` réutilisé sans modification, la
   phrase « Déduit du texte… » une fois par section au plus.
5. **M1**, **M3**, **M5**, **M6**, **M7** exécutés et consignés.

---

### PR-18 — `impacts.py` passe 1, étape `impacts`, helper `context()`

**Objectif.** Produire un brouillon d'analyses dans `review/`, à l'aveugle, hors
ligne, une requête batch par point.

**Fichiers modifiés**
- `pipeline/extract.py` — helper `context(text, quote, window)` : fenêtre de
  ±1500 caractères autour de la citation, découpée sur des frontières de mots.
- `pipeline/run.py` — `impacts` enregistré dans `STEPS`, **hors de `all`** (DT-28).

**Nouveaux fichiers**
- `pipeline/impacts.py` — `SYSTEM` et `SCHEMA` du §9.1 et §5.4, `build_requests`,
  `run_batch(requests) -> dict[str, dict]` (DT-29), écriture de
  `review/fr-2027-impacts-draft.json`.

**Dépendances.** PR-15 (forme du brouillon alignée sur le schéma validé).
Parallélisable avec PR-16 et PR-17 : aucun fichier commun.

**Risques**
- **DP-35, le risque central de cette PR.** Le `custom_id` porte le préfixe de
  formation (`lr-depense-publique`) ; le titre du document porte le nom de la
  formation ; le chemin du fichier programme aussi. Aucun des trois ne doit
  entrer dans le corps du message. C'est un risque de fuite silencieuse : rien
  dans la sortie ne le révèle.
- `context()` peut recouper une autre mesure de la même formation dans sa
  fenêtre. Sans conséquence sur la cécité — le document est celui de la mesure —
  mais la fenêtre doit rester bornée pour ne pas devenir le document entier.
- Sans identifiants d'API, l'étape doit sortir 0 avec un message, comme
  `generate.py` : la CI ne doit jamais dépendre d'un appel de modèle.

**Tests à ajouter**
- **A-9** : sur la sortie de `build_requests`, aucun identifiant, nom ou sigle de
  formation, aucun titre de document, aucun nom de fichier dans le corps des
  messages. Même mécanique de correspondance que `check_questions`.
- **A-16** : `--step all` n'exécute pas `impacts`.
- **A-17** : `impacts.py` n'a aucun chemin d'écriture hors de `ROOT / "review"`.
- `context()` : citation en début, en fin et au milieu du document ; citation
  absente ; découpe sur frontière de mot ; fenêtre plus large que le document.

**Critères d'acceptation**
1. `python -m pipeline.run --election fr-2027 --step impacts` sans identifiants
   sort 0 avec un message, sans rien écrire.
2. Avec identifiants, écrit un brouillon groupé par point, **citation en tête**,
   contexte documentaire à la suite.
3. **A-9**, **A-16**, **A-17** vérifiés.
4. Une seule fonction porte l'appel au fournisseur (DT-29) ; aucune interface,
   aucun adaptateur.
5. Aucune dépendance Python ajoutée — `anthropic` est déjà présent.

---

### PR-19 — Passe 2, annotations, régénération incrémentale

**Objectif.** Ajouter la couche d'audit, les annotations `lint` et `audit` du
brouillon, et le mécanisme qui rend une régénération à coût nul en régime stable.

**Fichiers modifiés**
- `pipeline/impacts.py` — prompt du §9.2, schéma du §5.5, fusion des verdicts dans
  le brouillon, calcul et comparaison de `of`, drapeaux `--limit N` et `--force`,
  annotation `lint` par appel à `neutrality`.
- `pipeline/run.py` — les deux drapeaux, si `argparse` doit les porter.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-18 (même fichier) et PR-16 (import de `neutrality`).

**Risques**
- **La passe 2 ne doit jamais voir le prompt de la passe 1** (DP-36). Un partage
  de constante entre les deux prompts est la façon naturelle de casser cela.
- **La passe 2 annote, ne supprime pas.** Un filtrage « pour alléger la
  relecture » masquerait la dérive du prompt, qui est précisément ce qu'il faut
  voir.
- `of` calculé ici et vérifié en L-03 par `check.py` : deux calculs du même
  condensé. Ils doivent partager la fonction, sinon ils divergeront — le motif
  déjà tranché par DT-18 et DT-26.
- Le champ `model` doit être écrit par le producteur, pas déduit à la relecture.

**Tests à ajouter**
- **A-15** : une deuxième exécution sans changement de contenu ne produit
  **aucune** requête.
- `--force` régénère malgré un `of` concordant ; `--limit N` plafonne le nombre
  de points traités.
- `of` : le condensé produit par `impacts.py` est celui qu'attend L-03, vérifié
  sur le corpus réel dans un test partagé par les deux modules.
- Le brouillon contient **tous** les énoncés produits, y compris ceux dont le
  verdict n'est pas `ok`.

**Critères d'acceptation**
1. **A-15** vérifié.
2. Aucune constante de prompt partagée entre les deux passes.
3. Le brouillon porte `lint` et `audit` par énoncé, et aucun énoncé n'a été
   retiré.
4. `python -m pipeline.check` reste vert : la PR n'écrit rien dans `content/`
   (**A-17** toujours vérifié).

---

### PR-20 — Première vague de contenu relu

**Objectif.** Livrer les analyses d'au moins **une question entièrement
couverte**, relues à la main, et faire de la fonctionnalité un fait observable.

**Fichiers modifiés**
- `content/impacts/fr-2027.json` — les entrées relues, chacune avec `of`, `model`,
  `reviewed`.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-15 et PR-16 (la CI doit pouvoir refuser), PR-17 (pour que le
contenu soit visible). PR-18 et PR-19 ne sont pas des dépendances dures : DP-33
et DP-36 admettent une entrée écrite entièrement à la main, `model: "manual"`.

**Risques**
- **Charge de relecture** (R-5) : c'est le coût dominant de la fonctionnalité, et
  il est porté par cette PR. Le découpage par question la borne — une question,
  jusqu'à quatre points, jusqu'à 40 énoncés.
- Une question dont une position manque n'affiche **rien** : de l'extérieur, cela
  ressemble à une panne. C'est le comportement voulu (DP-34) et la description de
  la PR doit le dire, sinon une session ultérieure « corrigera » le rendu.
- Le diff est du contenu, pas du code : il se relit énoncé par énoncé, jamais en
  survol.
- Tentation de choisir la question la plus facile à analyser. Le choix doit être
  une question **entièrement couverte**, pas une question commode.

**Tests à ajouter.** Aucun test de code. Cette PR est celle qui rend les tests
existants signifiants : **A-1** et **A-5** ne sont vérifiables qu'ici, sur un
corpus réel.

**Critères d'acceptation**
1. **A-1** : `python -m pipeline.check` passe sur un corpus comportant au moins
   une question entièrement couverte.
2. **A-5** : une question partiellement couverte n'affiche aucune analyse, et
   `check` émet W-01 sans échouer.
3. Chaque entrée porte `reviewed` à la date de la relecture effective, et `model`
   conforme à son mode de production.
4. Aucune entrée ne dépasse les bornes de DP-33 — vérifié par la CI, pas par
   appréciation.
5. Relecture manuelle consignée : chaque énoncé `text` a été confronté à son
   `span`, chaque énoncé `inferred` est conditionnel.

---

### PR-21 — Statut épistémique en méthodologie et documentation

**Objectif.** Rendre vrai dans l'interface ce qui devient vrai dans le dépôt
(P10, DP-38) : les analyses existent, elles sont assistées par modèle de langage,
une partie d'entre elles n'est pas vérifiable, et leur nombre est plafonné.

**Fichiers modifiés**
- `web/src/pages/[lang]/method.astro` — la déclaration dans la section des limites.
- `web/src/lib/ui.js` — extension de `methodModelFacts`, entrée dans
  `methodLimits`.
- `README.md` — un paragraphe.

**Nouveaux fichiers.** Aucun.

**Dépendances.** Aucune dure. À fusionner **après PR-20** en pratique : déclarer
un statut épistémique pour un contenu qui n'existe pas encore rend la page de
méthodologie fausse dans l'autre sens.

**Risques**
- **Recopier un plafond.** Les bornes de DP-33 sont dans le linter ; les publier
  en les réécrivant crée la seconde copie que DP-11 et DP-15 ont déjà interdite
  ailleurs. Si la page doit citer un chiffre, elle le lit ; sinon elle décrit la
  règle sans le chiffre.
- L'ordre des quatre faits de DP-17 est normatif : le fait le plus inquiétant en
  premier. L'extension ne doit pas se glisser en fin de liste pour adoucir.
- Aucune formule d'atténuation (« comme la plupart des outils »).

**Tests à ajouter.** Aucun test nouveau : `ui.test.mjs` couvre déjà la parité des
clés et l'absence de valeur vide, et les clés ajoutées y tombent
automatiquement.

**Critères d'acceptation**
1. La page déclare les quatre affirmations de DP-38, dont le fait que les
   analyses ne sont pas exhaustives.
2. Aucun plafond, seuil ou borne recopié depuis le code.
3. `npm test` passe sans modification des tests existants.
4. Les deux langues sont livrées ensemble (DP-18 : le chrome est traduit).

---

## 3 — Couverture des critères d'acceptation de la DP

| Critère | PR | Critère | PR |
|---|---|---|---|
| A-1 | 20 | A-10 | 17 |
| A-2 | 15 + 16 | A-11 | 17 |
| A-3 | 16 | A-12 | 17 |
| A-4 | 16 | A-13 | 17 |
| A-5 | 15 (W-01) + 20 | A-14 | 17 |
| A-6 | 15 | A-15 | 19 |
| A-7 | 17 | A-16 | 18 |
| A-8 | 17 | A-17 | 18 |
| A-9 | 18 | A-18 | 15 |

Les dix-huit critères sont couverts. Aucun n'est porté par deux PR sans que la
seconde ne le renforce sur un corpus réel.

---

## 4 — Points chauds et conflits

| Fichier | PR | Nature |
|---|---|---|
| `pipeline/check.py` | 15, 16 | **Point de conflit unique.** PR-16 insère l'appel du linter dans le code écrit par PR-15. Jamais simultanées. |
| `pipeline/impacts.py` | 18, 19 | Sérialisées par construction : PR-19 étend ce que PR-18 crée. |
| `web/src/lib/ui.js` | 17, 21 | Ajouts de clés dans des tables distinctes. Conflit mécanique, résolution triviale. |
| `web/src/styles.css` | 17 | Un bloc ajouté en fin de fichier. Aucune restructuration (DT-15). |
| `content/impacts/fr-2027.json` | 15, 20 | PR-15 crée le fichier vide, PR-20 le remplit. Aucune autre PR n'y touche. |

**Jamais touchés par ces sept PR :** `api/`, `web/src/pages/[lang]/index.astro`,
`Question.astro`, `AnswerScale.astro`, `score.js`, `check-blindness.mjs`,
`.github/workflows/`. Toute PR qui les modifie sort de son périmètre.

---

## 5 — Points non tranchés par la DP

Trois questions rencontrées pendant le découpage et **non résolues ici**, la DP
imposant de signaler plutôt que de trancher. La première bloque PR-15.

### 5.1 — Où vivent les cas de test Python — **bloquant pour PR-15**

**Constat.** A-2 exige un cas de test par règle, A-3 une fixture, A-4 une
auto-vérification. Le dépôt n'a **aucun test Python** : `requirements.txt`
déclare `requests`, `pypdf`, `anthropic` et rien d'autre, la commande `checks` de
`CLAUDE.md` n'en lance aucun, et `daily.yml` non plus. DT-26 ne prescrit
d'`assert` sous `__main__` que pour `neutrality.py`.

**Ce qui manque.** Les règles L-01 à L-10 et L-18/L-19 portent sur un fichier et
un corpus, pas sur une chaîne : elles ne tiennent pas dans l'auto-vérification
d'un module de lexique. Deux voies existent — `unittest` de la bibliothèque
standard dans `pipeline/`, ou une extension de la doctrine `assert` sous
`__main__` à `check.py`. Le choix engage la commande `checks` de `CLAUDE.md` et
les deux workflows.

**Ce n'est pas une décision de découpage.** Elle est laissée au responsable.

### 5.2 — Quelle constante de modèle fait autorité pour W-03

**Constat.** W-03 avertit sur une entrée dont `model` diffère du « modèle courant
du pipeline ». `generate.py` porte `MODEL = "claude-opus-5"` ; `impacts.py` en
portera un. `check.py` doit lire l'un des deux, ou un troisième.

**Impact.** Mineur, borné à une ligne de PR-15. Signalé pour qu'il ne soit pas
tranché en silence par la session qui implémentera.

### 5.3 — Capture de la référence octet à octet pour A-7

**Constat.** A-7 compare le HTML compilé avant et après. Le dépôt ne conserve
aucune référence, et `web/dist/` est ignoré. La procédure — construire sur la
base avant fusion, conserver l'empreinte, comparer — est celle de DT-20 et n'a
jamais été écrite comme procédure.

**Impact.** Procédural, pas conceptuel. À écrire dans la description de PR-17.

---

## 6 — Ce que ce plan ne fait pas

- **Il ne réordonne pas les décisions.** Toute divergence entre ce document et
  `DECISION.md` se tranche en faveur de `DECISION.md`.
- **Il n'ajoute aucune PR hors du périmètre de la DP.** Les vingt et un
  non-objectifs du §14 restent refusés sans réexamen.
- **Il ne traite pas OQ-03 ni OQ-04** (date de récolte, versionnement des items) :
  hors périmètre, comme pour le chantier précédent.
- **Il n'ajoute aucune dépendance**, npm ou Python (DT-01, §12 de la DP).
