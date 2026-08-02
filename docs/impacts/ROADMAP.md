# Civis — Découpage en PR : conséquences concrètes d'une mesure

**Objet.** Plan d'implémentation de `docs/impacts/DECISION.md`. Neuf PR,
numérotées **PR-15 à PR-23** : la numérotation prolonge celle du chantier
d'interface (PR-01 à PR-14, livré), comme DP-29 et DT-21 prolongent le registre
de décisions.

**Statut : figé.** La phase de conception est close. Les trois points que la
version précédente de ce document laissait ouverts sont tranchés par **DP-40**,
**DT-30** et **DT-31** (`DECISION.md` §17). **Aucune décision d'architecture ne
reste à prendre pendant les PR.** Une session qui en rencontre une s'arrête et
la signale — elle ne tranche pas, et elle ne « simplifie » pas la séquence.

**Règle de découpage appliquée.** Celle du chantier précédent, qui a marché :
l'outillage avant le chantier, le schéma avant les producteurs, la matière avant
son rendu, un point de conflit sérialisé explicitement. Une PR porte **une seule
responsabilité**.

---

## 1 — Vue d'ensemble

| PR | Objet | ~lignes | Dépend de |
|---|---|---|---|
| **PR-15** | Suite de tests Python (`unittest`) — outillage seul | 200 | — |
| **PR-16** | Schéma d'analyses, fichier vide, validation structurelle | 350 | 15 |
| **PR-17** | `neutrality.py` : lexique et règles lexicales | 400 | 16 |
| **PR-18** | `llm.py`, `impacts.py` passe 1 aveugle, étape `impacts` | 350 | 16 |
| **PR-19** | Passe 2, annotations, régénération incrémentale, **W-03** | 250 | 17, 18 |
| **PR-20** | **Corpus pilote relu** — quatre points, deux questions | 200–300 | 19 |
| **PR-21** | Rendu : `Impact.astro`, tout-ou-rien, libellés | 320 | 16, 20 |
| **PR-22** | Statut épistémique en méthodologie et documentation | 150 | 21 |
| **PR-23** | Génération complète, **par vagues** | variable | 20, 21, 22 |

```
PR-15 ──→ PR-16 ─┬→ PR-17 ─┬→ PR-19 ──→ PR-20 ──→ PR-21 ──→ PR-22 ──→ PR-23…
                 ├→ PR-18 ─┘                ↑
                 └────────────── PR-21 ─────┘  (PR-21 dépend aussi de PR-16
                                                 pour le fichier importé)
```

**Parallélisable :** PR-17 ∥ PR-18 (aucun fichier commun).
**Jamais simultanées :** 16 et 17 (`check.py`), 18 et 19 (`impacts.py`).

---

## 2 — Pourquoi cet ordre a changé

La version précédente plaçait le rendu (ancienne PR-17) avant les producteurs.
L'ordre est inversé : **le pipeline est validé de bout en bout avant que la
première ligne d'interface soit écrite.** Quatre raisons, par ordre de force.

**1. Les défaillances coûteuses sont toutes en amont.** Une fuite d'identité de
formation dans un prompt (DP-35), un lexique qui laisse passer un jugement de
valeur (INV-21), un brouillon illisible qui rend la relecture impraticable
(R-5) : ces trois défauts se paient en contenu à jeter et en confiance perdue.
Le rendu, lui, ne peut échouer que d'une façon visible à l'œil et rattrapable en
une PR.

**2. Écrire le rendu avant le contenu, c'est le tester contre un fichier vide.**
L'ancienne séquence livrait un composant dont le critère d'acceptation était
« n'affiche rien » — un critère qu'on ne peut pas rater et qui n'enseigne rien.
Avec PR-20 en amont, `Impact.astro` est vérifié contre des énoncés réels, des
`span` réels et une question à trois formations dès sa première exécution.

**3. Le pilote peut invalider le prompt ; il ne peut pas invalider le rendu.**
§9 de la DP : modifier un prompt invalide le contenu déjà relu. Ce risque doit
être purgé le plus tôt possible, sur quatre points et non sur cent vingt (DP-40).
Aucun risque symétrique n'existe côté interface.

**4. Le contenu commité a de la valeur sans interface.** Après PR-20, les
analyses sont dans `content/`, vérifiées par la CI, diffables — c'est-à-dire
déjà conformes à DP-06. L'interface n'est que leur exposition.

**Coût assumé.** La fonctionnalité reste invisible pour l'utilisateur jusqu'à
PR-21, soit sept PR. C'est le même arbitrage que PR-01 du chantier précédent, et
il se justifie de la même façon : ce qui protège un invariant passe avant ce qui
se voit.

---

## 3 — Les neuf PR

Chaque PR porte les cinq rubriques exigées : **critères d'acceptation**, **tests
à ajouter**, **invariants concernés**, **risques**, **revue manuelle**.

---

### PR-15 — Suite de tests Python (`unittest`)

**Objectif.** Doter le dépôt d'une vraie structure de tests Python (DT-30), et
rien d'autre. Aucune fonctionnalité, aucun fichier de contenu, aucun changement
de comportement. Les huit PR suivantes ont ainsi un endroit où écrire leurs
tests dès leur première ligne.

**Fichiers modifiés**
- `CLAUDE.md` — la commande `checks` s'allonge de `python -m unittest discover`.
- `.github/workflows/daily.yml` — job `checks`, une ligne.
- `.github/workflows/pages.yml` — une ligne, avant `npm test`.

**Nouveaux fichiers**
- `pipeline/tests/__init__.py`
- `pipeline/tests/test_extract.py` — premiers cas, sur le code aujourd'hui non
  testé dont tout le reste dépend : `normalise()`, `haystack()`, `flatten()`,
  `candidates()`.

**Dépendances.** Aucune.

**Invariants concernés**
- **INV-06** — `haystack()` est le mécanisme par lequel une citation est
  vérifiée mot pour mot. Il n'avait aucun test. Les cas écrits ici documentent
  ce que « verbatim » signifie exactement dans ce dépôt : espaces effondrés,
  typographie normalisée, saut de ligne de PDF sans effet.

**Risques**
- **Un échafaudage vide.** Une suite qui ne teste rien d'existant serait un
  fichier de plus. C'est pourquoi elle démarre sur `extract.py` : quatre
  fonctions pures, sans réseau, dont deux portent INV-06.
- **Découverte et imports relatifs.** `pipeline/` utilise `from .extract import`.
  La suite doit se découvrir depuis la racine du dépôt ; une invocation depuis
  `pipeline/` casse les imports. La commande retenue est fixée ici et ne se
  rediscute pas dans les PR suivantes.
- **Faux sentiment de couverture.** Cette PR ne teste ni `fetch.py`, ni
  `check.py`, ni `generate.py`. Elle ne le prétend pas : elle installe l'outil.

**Tests à ajouter**
- `normalise()` : apostrophes typographiques, espaces insécables, ligatures,
  tirets — chaque remplacement de la table a son cas.
- `haystack()` : une citation coupée par un saut de ligne est retrouvée ; une
  citation dont un mot diffère ne l'est pas.
- `flatten()` : une puce ouvre un paragraphe ; une ligne sans ponctuation
  terminale se poursuit dans la suivante.
- `candidates()` : bornes de longueur, déduplication, ordre préservé.

**Revue manuelle**
- Exécuter la commande `checks` complète de `CLAUDE.md` sur un dépôt propre.
- Casser volontairement une assertion et vérifier que la CI échoue — sans
  commiter la cassure. Une suite qui ne peut pas échouer ne teste rien.

**Critères d'acceptation**
1. `python -m unittest discover` passe depuis la racine du dépôt.
2. Les deux workflows exécutent la suite, et un échec de test échoue le job.
3. `CLAUDE.md` décrit la commande exacte.
4. Aucune dépendance ajoutée à `requirements.txt`.
5. Aucun fichier de `web/`, `api/` ou `content/` modifié. Aucun comportement du
   pipeline changé.

---

### PR-16 — Schéma d'analyses, fichier vide, validation structurelle

**Objectif.** Faire exister `content/impacts/fr-2027.json`, le charger en CI et
le valider sur tout ce qui ne demande pas de lexique : forme, bornes, ordre
canonique, cohérence avec `programs/` et `positions.json`.

**Fichiers modifiés**
- `pipeline/check.py` — chargement de `content/impacts/`, règles **L-01 à L-10**,
  **L-18**, **L-19**, avertissements **W-01 à W-04**, énumération `GROUPS`
  (22 valeurs, DT-27) à côté de `THEMES`.
- `content/README.md` — quatrième famille de fichiers, schéma, garanties CI.

**Nouveaux fichiers**
- `content/impacts/fr-2027.json` — `{"election": "fr-2027", "impacts": {}}`.
  Le fichier doit exister dès ici : PR-21 l'importera et un import manquant
  casse le build. Conséquence de découpage, pas décision — DP-34 rend
  `impacts: {}` sémantiquement correct.
- `pipeline/tests/test_impacts_schema.py`

**Dépendances.** PR-15 (les tests ont besoin de la suite).

**Invariants concernés**
- **INV-19** — L-04 et L-05 : un énoncé `text` porte un `span`, retrouvé verbatim.
- **INV-22** — L-08 : les bornes de DP-33, identiques pour toutes les formations.
- **INV-23** — L-18 : `reviewed` absent fait échouer la CI. C'est la trace du
  geste humain, et le seul mécanisme qui empêche un contenu généré d'entrer sans
  relecture.
- **INV-07** — les analyses vivent en JSON versionné, jamais en base.
- **INV-14** — W-02 avertit sur un point sans entrée ; il n'échoue pas. *Échouer
  sur ce qui est faux, avertir sur ce qui manque* (DT-26).

**Risques**
- **`pipeline/check.py` est le point de conflit unique côté pipeline**, ce que
  `styles.css` était côté web. **PR-16 et PR-17 ne peuvent pas être ouvertes
  simultanément** : PR-17 insère l'appel du linter dans le code écrit ici.
- Un chargement trop strict casse la CI sur un dépôt sans analyses. Atténuation :
  le fichier vide est livré dans la même PR, et W-02 avertit sur les ~120 points
  sans entrée sans faire échouer quoi que ce soit.
- `GROUPS` est écrit ici, ses libellés en PR-21 : deux déclarations séparées par
  cinq PR (DT-27). Le test de couverture qui les rapproche n'existe qu'en PR-21.
- L-19 (forme canonique) est la règle dont l'implémentation est la plus
  susceptible d'être approximative : sérialiser puis comparer **octet à octet**,
  y compris le saut de ligne final et `ensure_ascii=False`.

**Tests à ajouter**
- Un cas par règle portée — **L-01 à L-10, L-18, L-19** — chacun échouant avec un
  message **nommant la règle**.
- Forme canonique : un fichier correct se resérialise à l'identique (**A-18**) ;
  clés de points non triées, `items` hors ordre canonique, indentation ou saut de
  ligne final divergents échouent chacun.
- `of` : le condensé attendu est celui de la citation normalisée par
  `haystack()`, calculé dans le test depuis le corpus réel.
- Couverture partielle : une question dont une seule position porte une entrée
  produit **W-01** et un code de sortie 0 (**A-5**, part CI).
- Hors ligne : la vérification des `span` est **rapportée ignorée** (**A-6**).

**Revue manuelle**
- Lire les douze messages d'erreur. Un message qui ne nomme pas sa règle est
  inutilisable en relecture et doit être réécrit.
- Relire `content/README.md` : le schéma décrit doit être celui du §5.2 de la DP,
  sans reformulation approximative.

**Critères d'acceptation**
1. `python -m pipeline.check` passe sur le dépôt tel que livré, en affichant les
   avertissements W-02.
2. Chacune des douze règles portées échoue avec un message la nommant (**A-2**,
   part PR-16).
3. **A-18**, **A-6** et **A-19** vérifiés — ce dernier couvre les deux contrôles
   de schéma formalisés par DT-32 : `election` doit valoir le nom du fichier, et
   un fichier d'analyses absent échoue avec un message le nommant plutôt qu'avec
   une exception. W-02 est rapporté **agrégé**, pour le motif écrit en DT-32.
4. `--step all` inchangé ; aucun fichier de `web/` modifié ; sortie compilée
   identique octet à octet.
5. Aucune dépendance ajoutée.

---

### PR-17 — `pipeline/neutrality.py` : lexique et règles lexicales

**Objectif.** Rendre la neutralité opposable sur le contenu commité : le module
unique de DT-26, ses six lexiques, les règles portant sur les champs `fr` et
`en`.

**Fichiers modifiés**
- `pipeline/check.py` — import et appel de `neutrality`, sur les seuls champs
  `fr`/`en` — jamais un `span`, jamais une citation.

**Nouveaux fichiers**
- `pipeline/neutrality.py` — lexiques du §10.3 en clair, une entrée par ligne,
  triées ; règles **L-11 à L-17**. **Aucune auto-vérification sous `__main__`**
  (DT-30) : la couverture est dans la suite.
- `pipeline/tests/test_neutrality.py`

**Dépendances.** PR-16 (même fichier `check.py` ; les règles lexicales
s'appliquent à des entrées déjà validées structurellement).

**Invariants concernés**
- **INV-21** — c'est la PR qui l'institue. Aucun énoncé évaluatif dans le contenu
  commité, vérifié sur le produit et non sur le producteur.
- **INV-19** — L-14 et L-17 lisent le `span` pour décider : la preuve textuelle
  conditionne ce qu'un énoncé a le droit d'affirmer.

**Risques**
- **La liste d'exceptions par entrée.** Le vrai risque n'est pas le faux positif,
  c'est le contournement qui naîtra du premier blocage. Il est interdit
  (INV-21) et doit être refusé en revue, sans arbitrage.
- **L-14 et L-17 échouent en laissant passer**, pas en bloquant : ce sont les
  deux règles à état, et une erreur y est silencieuse.
- **Le lexique est un artefact éditorial** (R-4). Il est court, en clair, et se
  modifie par relecture — jamais pour débloquer une régénération.
- Le lexique anglais est plus faible que le français (R-7) : déclaré, non traité.

**Tests à ajouter**
- Un cas par règle : **L-11 à L-17**, avec le fragment fautif dans le message.
- **A-3** : les six exemples de la demande initiale en première fixture — les
  trois corrects passent ; « aidera énormément » échoue en **L-12**,
  « pénalisera » en **L-15**, « cette excellente réforme » en **L-12**. La
  correspondance est celle du §13 de la DP, corrigée à la livraison de PR-17
  pour décrire le comportement réel des règles.
- L-14 : quantificateur admis avec `basis: "text"` et un `span` qui le contient,
  refusé sans lui, refusé sur `inferred`.
- L-15 / L-16 : un énoncé `inferred` au futur de l'indicatif échoue, le même au
  conditionnel passe.
- **Non-application au `span`** : un terme évaluatif présent dans un `span` — donc
  dans le document officiel — ne fait pas échouer la CI.

**Revue manuelle**
- Lire les six lexiques mot à mot. C'est du contenu éditorial, pas du code.
- Passer le linter sur les 30 énoncés de questions existants pour mesurer le taux
  de faux positifs, et consigner le résultat dans la description de la PR. C'est
  la donnée qui rendra discutable, plus tard, une plainte contre le lexique.

**Critères d'acceptation**
1. **A-2** complet : les 19 règles L-01 à L-19 échouent chacune sous son nom.
2. **A-3** vérifié. **A-4** au sens amendé : la suite couvre `neutrality.py`
   règle par règle.
3. Le lexique n'est appliqué à aucun `span` ni à aucune citation.
4. Aucune liste d'exceptions par entrée nulle part.
5. Une seule déclaration du lexique dans le dépôt.

---

### PR-18 — `llm.py`, passe 1 aveugle, étape `impacts`

**Objectif.** Produire un brouillon d'analyses dans `review/`, à l'aveugle, hors
ligne, une requête par point — et fixer la configuration du fournisseur (DT-31).

**Fichiers modifiés**
- `pipeline/extract.py` — helper `context(text, quote, window)` : fenêtre de
  ±1500 caractères autour de la citation, découpée sur des frontières de mots.
- `pipeline/run.py` — `impacts` enregistré dans `STEPS`, **hors de `all`** (DT-28).

**Nouveaux fichiers**
- `pipeline/llm.py` — `PROVIDER` et `MODEL` (constantes surchargeables par
  l'environnement), dictionnaire `PROVIDERS`, implémentation Gemini par HTTP
  direct avec `requests`, fonction unique
  `run_batch(requests) -> dict[str, dict]` (DT-29, DT-31). Boucle synchrone :
  quatre points ne justifient pas l'API batch, et DT-29 l'admet explicitement.
- `pipeline/impacts.py` — `SYSTEM` et `SCHEMA` des §9.1 et §5.4, `build_requests`,
  écriture de `review/fr-2027-impacts-draft.json`.
- `pipeline/tests/test_impacts_generate.py`

**Dépendances.** PR-16 (forme du brouillon alignée sur le schéma validé).
Parallélisable avec PR-17 : aucun fichier commun.

**Invariants concernés**
- **INV-20 / DP-35** — l'aveuglement du générateur. Le `custom_id` porte le
  préfixe de formation, le titre du document porte son nom, le chemin du fichier
  programme aussi : aucun des trois n'entre dans le corps du message.
- **INV-23** — `impacts.py` ne connaît qu'un seul chemin d'écriture,
  `ROOT / "review"`.
- **INV-16** — aucune dépendance nouvelle ; l'appel réseau est hors ligne, jamais
  à l'exécution du site.

**Risques**
- **La fuite d'identité est silencieuse.** Rien dans la sortie ne la révèle :
  c'est le risque central de cette PR, et la seule protection est le test A-9.
- `context()` peut recouper une autre mesure de la même formation. Sans
  conséquence sur la cécité — le document est celui de la mesure — mais la
  fenêtre doit rester bornée pour ne pas devenir le document entier.
- **`generate.py` n'est pas migré vers `llm.py`** (DT-31). Le tenter serait un
  changement sans rapport avec l'objet de la PR.
- Sans identifiants, l'étape doit sortir 0 avec un message, comme `generate.py` :
  la CI ne dépend jamais d'un appel de modèle.
- Les réponses 429 et 5xx sont à gérer à la main, une fois, dans `llm.py` : coût
  assumé de l'absence de SDK.

**Tests à ajouter**
- **A-9** : sur la sortie de `build_requests`, aucun identifiant, nom ou sigle de
  formation, aucun titre de document, aucun nom de fichier dans le corps des
  messages — même mécanique de correspondance que `check_questions`.
- **A-16** : `--step all` n'exécute pas `impacts`.
- **A-17** : aucun chemin d'écriture hors de `review/`.
- `context()` : citation en début, en fin, au milieu ; citation absente ; découpe
  sur frontière de mot ; fenêtre plus large que le document.
- `llm.py` : `PROVIDERS` résout la configuration par défaut ; un nom de
  fournisseur inconnu échoue immédiatement, avec un message le nommant.

**Revue manuelle**
- Lire un brouillon réel : la citation est-elle bien en tête, le contexte
  lisible, l'unité de relecture praticable ? C'est l'ergonomie qui décidera du
  coût de PR-20.
- Vérifier à l'œil, sur une requête sérialisée, qu'aucun nom de formation n'y
  figure — le test A-9 protège, la lecture confirme.

**Critères d'acceptation**
1. Sans identifiants, `--step impacts` sort 0 avec un message, sans rien écrire.
2. Avec identifiants, écrit un brouillon groupé par point, **citation en tête**,
   contexte à la suite.
3. **A-9**, **A-16**, **A-17** vérifiés.
4. Une seule fonction porte l'appel au fournisseur ; aucun protocole, aucune
   classe d'adaptation.
5. `requirements.txt` inchangé.

---

### PR-19 — Passe 2, annotations, régénération incrémentale, W-03

**Objectif.** Ajouter la couche d'audit, les annotations `lint` et `audit` du
brouillon, le mécanisme qui rend une régénération gratuite en régime stable, et
l'avertissement **W-03** resté sans PR.

**Fichiers modifiés**
- `pipeline/impacts.py` — prompt du §9.2, schéma du §5.5, fusion des verdicts,
  calcul et comparaison de `of`, drapeaux `--limit N` et `--force`, annotation
  `lint` par appel à `neutrality`.
- `pipeline/run.py` — les deux drapeaux.
- `pipeline/check.py` — **W-03** : entrée dont `model` diffère de `llm.MODEL`.
  La règle est écrite au §10.2 de la DP depuis l'origine ; PR-16 ne pouvait pas
  la porter, faute de `llm.MODEL`, et a laissé un renvoi vers PR-18 dans le code.
  PR-18 ne l'a pas reprise : son périmètre ne comprenait pas `check.py`. Elle est
  rattachée ici, où le champ `model` est de toute façon en jeu — et le renvoi
  périmé de `check.py` disparaît avec elle.
- `pipeline/tests/test_impacts_generate.py` — étendu.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-18 (même fichier) et PR-17 (import de `neutrality`).

**Invariants concernés**
- **INV-23** — la passe 2 n'écrit toujours que dans `review/`.
- **INV-21** — le linter annote le brouillon ici, mais la garantie reste celle de
  la CI sur le contenu commité. L'annotation aide la relecture, elle ne la
  remplace pas.

**Risques**
- **La passe 2 ne doit jamais voir le prompt de la passe 1** (DP-36). Partager
  une constante entre les deux prompts est la façon naturelle de casser cela.
- **La passe 2 annote, ne supprime pas.** Un filtrage « pour alléger la
  relecture » masquerait la dérive du prompt, qui est ce qu'il faut voir.
- `of` est calculé ici et vérifié par L-03 dans `check.py` : deux calculs du même
  condensé. Ils partagent la fonction ou ils divergeront — motif déjà tranché par
  DT-18 et DT-26.
- Le champ `model` est écrit par le producteur, jamais déduit à la relecture.

**Tests à ajouter**
- **A-15** : une seconde exécution sans changement de contenu ne produit
  **aucune** requête.
- `--force` régénère malgré un `of` concordant ; `--limit N` plafonne le nombre
  de points traités.
- `of` : le condensé produit par `impacts.py` est celui qu'attend L-03, vérifié
  sur le corpus réel dans un test partagé par les deux modules.
- Le brouillon contient **tous** les énoncés produits, y compris ceux dont le
  verdict n'est pas `ok`.
- **W-03** : une entrée dont `model` diffère de `llm.MODEL` produit un
  avertissement et un code de sortie 0 ; la même entrée au modèle courant n'en
  produit aucun.

**Revue manuelle**
- Lire les verdicts de la passe 2 sur un brouillon réel : signale-t-elle des
  choses que le linter rate ? Si elle n'apporte rien, c'est le prompt du §9.2
  qu'il faut revoir — par une décision documentée, pas par retouche.
- Vérifier que les deux prompts ne partagent aucun texte.

**Critères d'acceptation**
1. **A-15** vérifié.
2. Aucune constante de prompt partagée entre les deux passes.
3. Le brouillon porte `lint` et `audit` par énoncé ; aucun énoncé retiré.
4. `python -m pipeline.check` reste vert : rien n'est écrit dans `content/`.
5. **W-03 est implémentée**, `llm.MODEL` faisant autorité (DT-31), et les quatre
   avertissements W-01 à W-04 du §10.2 ont désormais chacun leur code.

---

### PR-20 — Corpus pilote relu

**Objectif.** Livrer les analyses de **deux questions entièrement couvertes**
(DP-40) : une question portant les positions de trois formations, une question
mono-formation — environ quatre points. Valider la chaîne complète et **mesurer
ce qu'aucune conception ne pouvait prévoir** : le taux de rejet en relecture.

**Fichiers modifiés**
- `content/impacts/fr-2027.json` — les entrées relues, chacune avec `of`, `model`,
  `reviewed`.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-19. DP-33 et DP-36 admettent une entrée écrite entièrement à
la main (`model: "manual"`) : la génération est un confort, pas un prérequis.

**Invariants concernés**
- **INV-19** — chaque énoncé `text` a été confronté à son `span`, à la main,
  avant que la CI ne le confirme.
- **INV-21** — le contenu passe le linter sans qu'aucun lexique n'ait été touché.
- **INV-22** — les bornes s'appliquent identiquement aux quatre points.
- **INV-23** — c'est la PR qui incarne l'invariant : le transfert de `review/`
  vers `content/` est un geste humain, et cette PR **est** ce geste.

**Risques**
- **La charge de relecture est le coût dominant** (R-5) et elle est portée ici.
  Quatre points, jusqu'à 40 énoncés : c'est la borne que DP-40 existe pour poser.
- **Rien ne s'affiche encore** : le rendu arrive en PR-21. C'est voulu — le
  contenu est validé par la CI avant d'être exposé.
- **Choisir la question commode plutôt que la question couverte.** Le pilote doit
  contenir une question à trois formations : c'est le seul cas qui éprouve la
  règle du tout-ou-rien.
- Le diff est du contenu : il se relit énoncé par énoncé, jamais en survol.

**Tests à ajouter.** Aucun test de code. Cette PR est celle qui rend les tests
existants signifiants : **A-1** n'est vérifiable qu'ici, sur un corpus réel.

**Revue manuelle.** *La relecture est la PR.* Pour chaque énoncé : est-il
descriptif ? Le `span` le soutient-il réellement ? Un énoncé `inferred` est-il
bien conditionnel ? Procédure normative du §8 de la DP, point par point, citation
en tête.

**Critères d'acceptation**
1. **A-1** : `python -m pipeline.check` passe sur un corpus comportant au moins
   une question entièrement couverte.
2. **A-5** : une question partiellement couverte n'affiche aucune analyse et
   produit W-01 sans échec — vérifié sur l'état réel du dépôt.
3. Chaque entrée porte `reviewed` à la date de la relecture **effective**, et
   `model` conforme à son mode de production.
4. Aucune entrée ne dépasse les bornes de DP-33 — vérifié par la CI, jamais par
   appréciation.
5. **Le taux de rejet en relecture est mesuré et consigné dans la description de
   la PR.** C'est la donnée qui autorisera ou non PR-23 (DP-40).
6. Aucun lexique modifié pour faire passer une entrée.

---

### PR-21 — Rendu : `Impact.astro`, tout-ou-rien, libellés et vocabulaire

**Objectif.** Afficher une analyse quand la question est entièrement couverte, et
rien du tout sinon. Zéro octet de JavaScript ajouté.

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
- `web/src/lib/impacts.js` — la règle tout-ou-rien, `fullyAnalysed(entries,
  impacts)`. *Ajouté à la livraison :* la règle décide ce que trente questions
  affichent et ses deux modes de défaillance sont silencieux ; écrite en lambda
  dans `results.astro` elle n'était exécutable ni sans navigateur ni sans build.
  Un module d'une fonction, à côté de `score.js`, la rend testable sans rien
  changer d'autre — ce n'est pas une abstraction, c'est le même précédent que
  `score.js` pour la même raison.
- `web/src/lib/impacts.test.mjs` — cas de la règle, plus la propriété vérifiée
  sur le corpus livré.

**Dépendances.** PR-16 (le fichier importé doit exister) et PR-20 (du contenu
réel à rendre — c'est la raison du nouvel ordre, §2).

**Invariants concernés**
- **INV-20** — le vecteur nommé par la DP est l'import des analyses dans un
  composant partagé entre les deux pages. `Impact.astro` est importé par
  `results.astro` et par rien d'autre, comme `Quote` et `Source`.
- **INV-12** — aucune couleur, aucun pictogramme, aucun badge : la distinction
  `text` / `inferred` est portée par la présence du fragment source.
- **INV-14** — une section vide n'est pas rendue, pas même son titre.
- **INV-17** — l'ordre de tabulation reste l'ordre visuel dans un bloc ouvert.
- **INV-06** — `<Quote>` est réutilisé sans modification : le `span` reste en
  français, avec son attribut de langue, jamais traduit.
- **INV-16** — aucune dépendance, aucune requête ajoutée.

**Risques**
- **`<details>` imbriqué dans `<details>`.** Le bloc s'ouvre à l'intérieur du
  `<details>` de question. Le comportement natif est correct, mais c'est le point
  où l'ordre de tabulation peut se dissocier de l'ordre visuel.
- Le volume HTML de la page de résultats croît. Assumé, comme en PR-10 : la
  contrepartie est zéro requête et zéro script.
- Le regroupement par `kind` est une opération de rendu (DT-22), jamais une
  structure de données. Trois sections typées dans le JSON seraient une
  régression de schéma.
- Densité : jusqu'à dix énoncés sous une position. Le pilote de PR-20 est ce qui
  permet de le constater à l'œil avant que 120 points ne soient produits.

**Tests à ajouter**
- Parité des clés `GROUPS.fr` / `GROUPS.en` — obtenue par ajout à `TABLES`, les
  trois tests génériques existants s'appliquent sans ligne nouvelle.
- Couverture : toute valeur `who` présente dans `content/impacts/` possède un
  libellé dans les deux langues (DT-27).
- Les tests de jetons et de contraste existants passent **sans modification**
  (**A-12**).
- **Règle tout-ou-rien** — *ajouté à la livraison.* Cas de la règle : question
  entièrement couverte, partiellement couverte, non couverte, sans position,
  et la bascule que PR-23 produit vague après vague. Plus deux propriétés
  vérifiées sur le corpus livré, sans nommer aucune question — une question
  affichée a **toutes** ses positions analysées, une question partiellement
  analysée est **muette** — de sorte que les vagues de PR-23 n'aient jamais à
  retoucher le test.

**Revue manuelle**
- **M1** — parcours clavier complet, bloc ouvert et fermé (**A-13**).
- **M3** — 320 px : aucun défilement horizontal.
- **M5** — contraste forcé : le bloc reste distinguable sans couleur.
- **M6** — thèmes clair et sombre.
- **M7** — **JavaScript désactivé** : les blocs s'ouvrent et se ferment (**A-10**).
- Lecture des règles U-01 à U-09 sur le rendu réel du pilote.

**Critères d'acceptation**
1. **A-7** : le HTML compilé de `<lang>/index.html` est identique **octet à
   octet** avant et après. Protocole DT-20 ; la référence est construite sur la
   base avant fusion et son empreinte consignée dans la description de la PR.
2. **A-8**, **A-10**, **A-11** (zéro octet de JS ajouté, zéro requête), **A-12**,
   **A-13**, **A-14**.
3. Les questions du pilote affichent leur analyse ; les vingt-huit autres
   n'affichent rien.
4. U-01 à U-09 vérifiés par lecture.

---

### PR-22 — Statut épistémique en méthodologie et documentation

**Objectif.** Rendre vrai dans l'interface ce qui est devenu vrai dans le dépôt
(P10, DP-38) : les analyses existent, elles sont assistées par un modèle de
langage, une partie n'est pas vérifiable, et leur nombre est plafonné.

**Fichiers modifiés**
- `web/src/pages/[lang]/method.astro` — la déclaration, dans la section des
  limites.
- `web/src/lib/ui.js` — extension de `methodModelFacts`, entrée dans
  `methodLimits`.
- `README.md` — un paragraphe.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-21. Déclarer un statut épistémique pour un contenu invisible
rendrait la page fausse dans l'autre sens.

**Invariants concernés**
- **INV-15** — contenu en français, identifiants en anglais.
- **INV-13** — aucun nombre sans sa base : si la page cite un plafond, elle le
  lit ; elle ne le recopie pas.

**Risques**
- **Recopier un plafond.** Les bornes de DP-33 vivent dans le linter. Les publier
  en les réécrivant crée la seconde copie que DP-11 et DP-15 ont déjà interdite
  ailleurs.
- L'ordre des quatre faits de DP-17 est normatif : le plus inquiétant en premier.
  L'extension ne se glisse pas en fin de liste pour adoucir.
- Aucune formule d'atténuation (« comme la plupart des outils »).

**Tests à ajouter.** Aucun test nouveau : `ui.test.mjs` couvre déjà la parité des
clés et l'absence de valeur vide ; les clés ajoutées y tombent automatiquement.

**Revue manuelle**
- Relire la section des limites en entier, dans les deux langues. C'est du texte,
  il se relit comme du texte.
- Vérifier qu'aucun chiffre de la page ne duplique une valeur du code.

**Critères d'acceptation**
1. Les quatre affirmations de DP-38 sont présentes, dont le fait que les analyses
   ne sont pas exhaustives.
2. Aucun plafond, seuil ou borne recopié depuis le code.
3. `npm test` passe sans modification des tests existants.
4. Les deux langues sont livrées ensemble.

---

### PR-23 — Génération complète, par vagues

**Objectif.** Étendre les analyses au reste du corpus, **une vague de questions
par PR**, une fois le pipeline jugé stable.

**Fichiers modifiés**
- `content/impacts/fr-2027.json` — les entrées de la vague.

**Nouveaux fichiers.** Aucun.

**Dépendances.** PR-20, PR-21, PR-22, **et les quatre conditions de stabilité de
DP-40** :
1. aucun lexique raccourci, aucune exception par entrée introduite ;
2. aucun prompt modifié depuis le pilote — sinon le contenu relu est invalidé ;
3. taux de rejet du pilote mesuré et jugé acceptable par le responsable ;
4. **A-15** vérifié en conditions réelles.

**Invariants concernés.** Les mêmes que PR-20 : INV-19, INV-21, INV-22, INV-23.

**Risques**
- **La fatigue de relecture.** C'est le risque qui croît avec le volume et le
  seul contre lequel aucun test ne protège. Le découpage par vagues est la
  réponse : une PR qui dépasse ~400 lignes de JSON se scinde.
- **La tentation d'assouplir** pour finir une vague. Une entrée qui ne passe pas
  se réécrit ou se supprime ; le lexique ne bouge pas.
- **La dérive de modèle.** W-03 signale une entrée produite par un autre modèle
  que `llm.MODEL`. Une vague produite après un changement de modèle est une vague
  à relire entièrement, pas à valider par continuité.

**Tests à ajouter.** Aucun. Comme PR-20, cette PR consomme les garanties
existantes.

**Revue manuelle.** La relecture point par point du §8, pour chaque point de la
vague. Aucun raccourci n'est prévu et aucun ne sera ajouté.

**Critères d'acceptation**
1. Les quatre conditions de DP-40 sont explicitement vérifiées et consignées dans
   la description de la première PR de la série.
2. `python -m pipeline.check` passe ; aucun avertissement W-01 sur les questions
   de la vague.
3. Chaque question livrée est **entièrement** couverte.
4. Le taux de rejet de la vague est consigné, comme pour le pilote.

---

## 4 — Couverture des critères d'acceptation de la DP

| Critère | PR | Critère | PR |
|---|---|---|---|
| A-1 | 20 | A-10 | 21 |
| A-2 | 16 + 17 | A-11 | 21 |
| A-3 | 17 | A-12 | 21 |
| A-4 *(amendé DT-30)* | 15 + 17 | A-13 | 21 |
| A-5 | 16 (W-01) + 20 | A-14 | 21 |
| A-6 | 16 | A-15 | 19 |
| A-7 | 21 | A-16 | 18 |
| A-8 | 21 | A-17 | 18 |
| A-9 | 18 | A-18 | 16 |
| — | — | A-19 *(ajouté DT-32)* | 16 |

Les dix-neuf critères sont couverts. Les deux critères portés par deux PR le sont
parce que la seconde les vérifie sur un corpus réel plutôt que sur une fixture.

---

## 5 — Points chauds et conflits

| Fichier | PR | Nature |
|---|---|---|
| `pipeline/check.py` | 16, 17, 19 | **Point de conflit unique.** Jamais simultanées. 19 n'y ajoute que W-03. |
| `pipeline/impacts.py` | 18, 19 | Sérialisées par construction. |
| `pipeline/tests/` | toutes | Un fichier par domaine, jamais un fichier commun. |
| `web/src/lib/ui.js` | 21, 22 | Ajouts de clés dans des tables distinctes. |
| `web/src/lib/impacts.js` | 21 | Une fonction, un appelant. Aucune PR ultérieure ne la touche. |
| `web/src/styles.css` | 21 | Un bloc ajouté en fin de fichier (DT-15). |
| `content/impacts/fr-2027.json` | 16, 20, 23 | 16 crée le fichier vide ; 20 et 23 le remplissent. |

**Jamais touchés par ces neuf PR :** `api/` (DT-10),
`web/src/pages/[lang]/index.astro`, `Question.astro`, `AnswerScale.astro`,
`score.js`, `check-blindness.mjs`, `pipeline/generate.py`, `pipeline/fetch.py`.
Toute PR qui les modifie sort de son périmètre.

---

## 6 — Ce que ce plan ne fait pas

- **Il ne réordonne pas les décisions.** Toute divergence entre ce document et
  `DECISION.md` se tranche en faveur de `DECISION.md`.
- **Il n'ajoute aucune PR hors du périmètre de la DP.** Les vingt et un
  non-objectifs du §14 restent refusés sans réexamen.
- **Il ne traite pas OQ-03 ni OQ-04** (date de récolte, versionnement des items) :
  hors périmètre, comme pour le chantier précédent.
- **Il n'ajoute aucune dépendance**, npm ou Python. `unittest` et `requests` sont
  déjà disponibles (DT-30, DT-31).
- **Il ne migre pas `generate.py`** vers `llm.py` : ce serait un changement sans
  rapport avec l'objet d'une PR de cette liste.
