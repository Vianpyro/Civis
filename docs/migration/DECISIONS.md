# Civis — Registre des décisions

**Objet :** une entrée par décision, avec son contexte, sa justification, ses conséquences, les alternatives rejetées et son impact sur les PR.
**Règle d'usage :** aucune décision de ce registre ne se réinterprète. Une session qui pense qu'une décision est mauvaise ne la modifie pas : elle le signale et s'arrête.

**Datation.** Le projet n'a pas de journal de décisions antérieur à ce registre. Les décisions marquées *(fondatrice)* préexistent au chantier et sont documentées dans `CLAUDE.md` et `README.md`. Les autres ont été arrêtées pendant l'analyse de refonte ; aucune date précise n'est disponible et aucune n'est inventée.

---

# Sommaire

- [Décisions produit — DP-01 à DP-25](#décisions-produit)
- [Décisions techniques — DT-01 à DT-20](#décisions-techniques)

---

# Décisions produit

## DP-01 — Aveuglement total avant la révélation *(fondatrice)*

**Décision.** Aucune affiliation — nom, sigle, logo, couleur, indice — n'atteint le client avant que l'utilisateur ait répondu à tout.

**Contexte.** Beaucoup de gens votent pour une étiquette avant de voter pour des idées. Retirer l'étiquette pendant qu'on se positionne retire le biais d'appartenance.

**Justification.** C'est la raison d'être du produit. Sans elle, Civis est un quiz politique de plus.

**Conséquences.** L'aveuglement est **structurel et non déclaratif** : `web/src/pages/[lang]/index.astro` n'importe que `content/questions/fr-2027.json`, qui ne contient aucune donnée de formation. La page ne *peut pas* révéler ce qu'elle ne contient pas. Les données de formation ne sont importées que par `results.astro`.

**Alternatives rejetées.** Masquer les noms côté affichage tout en les embarquant dans le bundle : rejeté parce que la garantie deviendrait déclarative, donc invérifiable, et cassable par une erreur de rendu.

**Impact PR.** PR-01 en fait un test. Toutes les autres doivent le préserver.

---

## DP-02 — Aucune statistique agrégée pendant le questionnaire *(fondatrice)*

**Décision.** Aucun agrégat n'est affiché avant la révélation.

**Contexte.** Afficher « 78 % sont d'accord » avant que l'utilisateur ait répondu réintroduit le biais de conformité.

**Justification.** C'est exactement le biais que l'outil sert à supprimer, une étape plus loin dans le parcours.

**Conséquences.** Les compteurs ne sont sollicités que depuis `results.astro`. Aucun appel réseau depuis le questionnaire, hormis l'envoi des réponses à la soumission.

**Alternatives rejetées.** Afficher les agrégats après réponse à chaque question : rejeté, cela contaminerait les réponses suivantes.

**Impact PR.** PR-12.

---

## DP-03 — Aucun résultat individuel stocké ; incréments indépendants *(fondatrice)*

**Décision.** Chaque réponse remonte en incrément **indépendant**. Rien ne relie entre elles les réponses d'une même personne.

**Contexte.** Grouper les réponses d'une personne constituerait un profil d'opinions politiques.

**Justification.** C'est ce qui garde le projet hors du champ de l'article 9 du RGPD : nous ne constituons jamais un profil, même transitoirement.

**Conséquences.** `index.astro:104-111` émet une requête par réponse, dans un ordre aléatoire, avec `keepalive`. La table SQLite n'a aucune colonne permettant de rapprocher deux réponses. **Ne pas grouper pour ajouter des corrélations.**

**Alternatives rejetées.** Un envoi groupé unique : plus simple et plus économe en requêtes, rejeté parce qu'il reconstituerait un profil dans la requête elle-même.

**Impact PR.** PR-09 doit exposer ce mécanisme à l'utilisateur sans le modifier.

---

## DP-04 — Agrégation par défaut, opt-out *(fondatrice, réaffirmée)*

**Décision.** La contribution aux statistiques est **activée par défaut**, désactivable d'une case. Refuser n'envoie rien du tout.

**Contexte.** L'analyse a explicitement mis en cause cette décision : une case pré-cochée est, en forme, le patron que les utilisateurs associent aux pratiques manipulatoires, sur un produit dont l'argument entier est l'absence de manipulation.

**Justification retenue.** La décision est **maintenue** : les compteurs sont anonymes et non corrélés, le dispositif est juridiquement solide, et l'invariant est déclaré dans `CLAUDE.md`. Changer un invariant écrit pour une raison de forme est une décision plus lourde qu'il n'y paraît.

**Conséquences.** L'opt-out n'est acceptable **que si** l'explication est lisible au moment de la décision. Le libellé doit énoncer un **état** (« vos réponses seront ajoutées… ») et non une proposition (« ajouter mes réponses… ») : un lecteur pressé qui lit une proposition croit refuser en ne faisant rien, alors qu'il accepte.

**Alternatives rejetées.**
- **Opt-in** : cohérence de forme parfaite, rejeté pour des agrégats beaucoup plus creux et biaisés vers les moins soucieux de confidentialité. L'argument « il faut du volume pour être représentatif » a été explicitement écarté comme non valable : l'échantillon est de toute façon auto-sélectionné.
- **Aucun défaut** (deux actions explicites) : la plus alignée sur le principe de ne décider à la place de personne, rejetée parce qu'elle impose une décision à qui n'en a pas, ce qui est aussi une forme de contrainte.

**Impact PR.** PR-09.

---

## DP-05 — Chaque question porte son document officiel et sa citation exacte *(fondatrice)*

**Décision.** La page de résultats affiche, pour chaque position, la citation exacte et l'URL du document officiel. La CI échoue si une citation n'apparaît pas mot pour mot dans le document cité.

**Justification.** La neutralité est vérifiée par une machine, pas affirmée dans un README.

**Conséquences.** `pipeline/check.py` porte cette vérification. Aucune citation ne peut être tronquée par la mise en page : une citation raccourcie est une citation altérée.

**Impact PR.** PR-10 (composants Citation et Source), PR-13.

---

## DP-06 — Git est la source de vérité ; SQLite ne contient que des compteurs *(fondatrice)*

**Décision.** Programmes, questions et empreintes vivent en JSON versionné. SQLite ne contient que des entiers.

**Justification.** L'historique diffable est un argument de transparence, pas un détail. Si la base disparaît, on perd des statistiques, jamais le produit.

**Impact PR.** Aucune PR ne remet ceci en cause. DT-10 en découle.

---

## DP-07 — Pas de page d'accueil ; le questionnaire est la page d'entrée

**Décision.** Aucune landing n'est créée. L'utilisateur atterrit directement sur le questionnaire.

**Contexte.** Une page d'accueil avait d'abord été recommandée, puis abandonnée après examen.

**Justification.** Une telle page ne contiendrait **que des affirmations sur nous-mêmes** (aveuglement, vie privée, sources), alors que le projet repose sur la preuve vérifiable et non sur la déclaration — substituer la rhétorique à la preuve est l'inverse de la posture du projet (P1). Structurellement, hero + arguments + bouton unique est le patron canonique de la page de conversion, ce qui viole la contrainte « ne pas transformer le site en application marketing ». Enfin, atterrir directement sur l'instrument est le geste le plus honnête : un site dont la page d'accueil *est* le travail se lit comme sérieux.

**Conséquences.** Le taux de démarrage cesse d'être définissable — assumé. Les besoins réels qu'une landing aurait servis sont redistribués : l'engagement annoncé va dans **l'en-tête du questionnaire (DP-27)**, le besoin d'inspection du sceptique va dans une page de méthodologie, qui est de la **documentation** et non de la conversion.

**Alternatives rejetées.** Landing séparée avec méthodologie repliée dessous : rejetée pour les motifs ci-dessus.

**Impact PR.** PR-13 (méthodologie), PR-07 (en-tête, DP-27).

---

## DP-08 — Page unique, pas de wizard

**Décision.** Les 30 questions restent sur une page unique défilante.

**Justification principale.** Une page unique rend **l'instrument auditable pendant son utilisation** : l'utilisateur peut lire les 30 questions avant d'en répondre une seule, revenir en arrière, comparer deux formulations, vérifier qu'aucune n'est orientée, imprimer la page, la partager telle quelle. Un wizard cache l'instrument au sujet pendant qu'il le subit, contrôle le rythme et masque combien il reste sans qu'on puisse le vérifier. Pour un questionnaire d'opinion politique, c'est la différence entre un document et un dispositif.

**Justifications secondaires.** Coût de maintenance pour un mainteneur unique ; risque de régression d'accessibilité sur la gestion du focus à chaque transition ; historique de navigation ; registre du quiz de divertissement.

**Conséquences assumées.** Longueur perçue à l'ouverture, défilement important en mobile, abandon en milieu de parcours qui perd tout — ce dernier point est traité par DP-09.

**Alternatives rejetées.** Wizard une-question-par-écran : gagne sur la charge cognitive par écran et la mesure fine de l'abandon ; **écarté par principe**, pas par arbitrage de coût.

**Impact PR.** PR-06, PR-07, PR-08.

---

## DP-09 — Brouillon en `sessionStorage`, restauration signalée

**Décision.** Les réponses en cours sont conservées en `sessionStorage`, restaurées avec un bandeau visible, effaçables à tout moment, effacées à la soumission. **Jamais `localStorage`.**

**Contexte.** L'analyse hésitait, au motif que stocker des opinions politiques sur l'appareil touche à un invariant.

**Justification.** Un fait tranche : `sessionStorage` est **déjà utilisé** (`index.astro:114`, clé `civis:answers`) pour transmettre les réponses à la page de résultats. Un enregistrement complet existe donc déjà sur l'appareil, pour la durée de l'onglet. Écrire dans la même clé à chaque changement ne crée **aucune donnée nouvelle, aucune clé nouvelle, aucune durée de vie nouvelle**. Le delta de vie privée est proche de zéro. À l'inverse, perdre 25 réponses sur un rechargement est une atteinte à la confiance autant qu'à la complétion.

**Conséquences — conditions non négociables.**
1. `sessionStorage` uniquement : la trace meurt à la fermeture de l'onglet.
2. Restauration **accompagnée d'un bandeau visible**. Une restauration silencieuse ferait retrouver à l'utilisateur des réponses qu'il ne se souvient pas d'avoir données — c'est exactement le défaut corrigé par DP-25, reproduit sous une autre forme.
3. Effacement disponible **à tout moment**, pas seulement au moment de la restauration.
4. Effacement automatique après la soumission.

**Alternatives rejetées.** `localStorage` (trace persistante) ; restauration silencieuse (voir ci-dessus) ; aucune persistance (perte de travail).

**Impact PR.** PR-08. Combiné à DP-14, impose DT-09.

---

## DP-10 — Résultat en fraction explicite ; ni pourcentage, ni barre, ni rang

**Décision.** Le résultat par formation s'exprime en **fraction explicite** : nombre de propositions sur lesquelles l'utilisateur rejoint la formation, sur le nombre de propositions effectivement comparées. Suppression du pourcentage, de la barre et du marquage de rang.

**Contexte.** Le corpus mesuré donne des dénominateurs de 4 (`lr`) à 19 (`nfp`), et 14 questions sur 30 ne concernent qu'une seule formation. La formule actuelle `(sum/weight + 1)/2` ramène tout utilisateur modéré autour de 50 %.

**Justification.** Le score n'est pas seulement imprécis, il est **faux dans une direction connue** : il récompense mécaniquement la couverture du corpus. Une mise en garde, même bien placée, ne bat jamais un grand nombre — l'utilisateur retient « 75 % LR ». Une fraction met le dénominateur **dans la phrase** : « 3 sur 4 » signale sa propre fragilité mieux que n'importe quel avertissement rédigé par nous, et rend inutile un seuil de fiabilité que nous aurions fixé à la place du lecteur.

**Conséquences.** Perte de la pondération par intensité : « tout à fait d'accord » et « plutôt d'accord » comptent pareil. **Compromis assumé** — une nuance dont le dénominateur varie de 4 à 19 n'est pas une nuance. Les réponses neutres et sautées réduisent simplement le dénominateur, ce qui est exactement leur sens. La révélation est moins spectaculaire : assumé, le spectacle était du côté du faux. Effet secondaire positif : `score.js` se simplifie.

Une marque graphique reste admise, à **remplissage uniforme**, et sa longueur maximale représente **le dénominateur propre à cette formation**, jamais un maximum commun : une échelle commune entre 4 et 19 est une affirmation d'équivalence.

**Alternatives rejetées.**
- **Garder le pourcentage avec des mises en garde** : rejeté, une note ne bat pas un grand nombre.
- **Ne rien afficher du tout** : intellectuellement le plus défendable, rejeté par DP-19 — l'utilisateur repartirait sans réponse et un outil qui refuse de conclure est perçu comme se dérobant.
- **Seuil de fiabilité masquant les formations peu couvertes** : rendu inutile par la fraction.

**Impact PR.** PR-11.

---

## DP-11 — Niveau de confiance qualitatif, plafonné, issu d'une règle publiée

**Décision.** Chaque résultat affiche un niveau de confiance qualitatif, déterminé par une règle publiée et déterministe fondée sur la base de comparaison. Le haut de l'échelle est **plafonné** : le corpus actuel ne peut soutenir aucune qualification supérieure à « partielle ».

**Justification.** Un score sans qualification est présenté comme une vérité absolue. Une échelle de confiance dont le sommet est inatteignable n'est pas une modestie de façade : c'est la description exacte de ce que l'instrument peut produire avec un corpus déséquilibré.

**Conséquences.** Le niveau est un **mot**, jamais une nuance, une couleur, une pastille ou une position graphique (INV-12). Il apparaît **toujours avec sa base numérique**. La règle et ses bornes doivent exister **à un seul endroit du code** et être décrites en méthodologie ; un seuil dupliqué divergera.

## Bornes arrêtées — définitives

La règle porte sur la **base de comparaison** : le nombre de propositions sur lesquelles l'utilisateur
s'est positionné de façon non neutre **et** sur lesquelles la formation possède une position.
Ce n'est pas la couverture, qui est une propriété du corpus (DP-12).

| Base de comparaison | Libellé affiché | Nature |
|---|---|---|
| **0** | « aucune comparaison » | **État**, pas un niveau de confiance |
| **1 – 4** | « très faible » | Niveau |
| **5 – 9** | « faible » | Niveau |
| **≥ 10** | « partielle » | Niveau — **plafond de l'échelle** |

**Aucun palier au-dessus de « partielle » n'existe ni n'existera** tant que la présente décision n'est
pas modifiée : c'est le plafonnement exigé ci-dessus.

**D'où viennent ces bornes.** Elles ne sont pas choisies pour leur rondeur : **chacune est une valeur
de couverture réellement mesurée dans le corpus `fr-2027`**, documentée en `MIGRATION.md` §8.

- **4** est la couverture de la formation la moins couverte du corpus (`lr` : 4 propositions sur 30).
  En deçà ou à ce niveau, la base de comparaison est inférieure ou égale à *tout ce que le corpus
  offre* pour une formation entière. C'est le régime où le résultat est dominé par les artefacts du
  jeu de données plutôt que par les opinions de l'utilisateur.
- **10** est la couverture de la formation médiane (`ensemble` : 10 propositions sur 30). Atteindre
  10 comparaisons signifie que la base égale l'intégralité du corpus disponible pour une formation
  de couverture moyenne.
- **0** est isolé parce que INV-14 impose qu'une absence s'affiche comme absence, et parce que DP-19
  interdit tout seuil minimal de calcul : une formation sans proposition comparée **s'affiche**, avec
  la raison de son état, jamais masquée.

**Conséquences assumées, à ne pas « corriger » ultérieurement.**

1. **`lr` (couverture 4) ne peut jamais dépasser « très faible »**, quelles que soient les réponses.
   Ce n'est pas un défaut de la règle : c'est la description exacte de ce que le corpus permet
   d'affirmer sur cette formation, rendue visible comme P5 l'exige.
2. **`ensemble` (couverture 10) n'atteint « partielle » que si l'utilisateur se positionne de façon
   non neutre sur ses 10 propositions.** Seuil atteignable, mais tout juste.
3. `nfp` (19) et `rn` (15) atteignent « partielle » à partir de 10 comparaisons.
4. Les bornes sont **relatives au corpus actuel**. Si la couverture change, la question de leur
   révision se pose — par une modification explicite de la présente décision, jamais par ajustement
   silencieux.

**Alternatives rejetées.**
- Un indicateur numérique de confiance (intervalle, marge d'erreur) : rejeté, il ajouterait une
  seconde précision fictive par-dessus la première.
- **Des bornes rondes (5 / 10 / 20)** : rejetées parce qu'elles auraient été arbitraires, donc
  indéfendables devant un lecteur qui demande « pourquoi 5 ». Une borne égale à une couverture
  mesurée se justifie par un fait du corpus, pas par une préférence.
- **Une échelle à deux paliers seulement** (« très faible » / « partielle ») : rejetée, elle place
  dans la même catégorie une base de 5 et une base de 9, alors que la seconde couvre la totalité de
  la couverture de `lr` deux fois.
- **Un palier au-dessus de « partielle »** : interdit par le plafonnement, quel que soit le nombre de
  comparaisons — même 19 sur 19 ne permet pas d'affirmer davantage avec un corpus déséquilibré.

**Emplacement dans le code.** La règle et ses bornes vivent dans `web/src/lib/score.js`, **à un seul
endroit**, exportées pour que PR-13 les lise sans les recopier (DT-18, et critère « seuils affichés =
seuils du code » de PR-13).

**Impact PR.** PR-11 (implémentation et tests aux bornes 0, 1, 4, 5, 9, 10), PR-13 (publication).

---

## DP-12 — Couverture du corpus toujours visible

**Décision.** Chaque résultat affiche la couverture du corpus par la formation : sur combien des propositions du questionnaire elle possède une position identifiée, **indépendamment des réponses de l'utilisateur**.

**Justification.** C'est une propriété du jeu de données, distincte de la base de comparaison personnelle. Sa disparité entre formations (4 / 10 / 15 / 19) est la principale limite du produit, et P5 impose de l'afficher de notre propre initiative.

**Conséquences.** Deux nombres coexistent sur chaque résultat et ne doivent jamais être confondus : **couverture** (propriété du corpus) et **base de comparaison** (propriété de la passation). Le glossaire de `MIGRATION.md` fixe les deux termes.

**Impact PR.** PR-11.

---

## DP-13 — Limites méthodologiques affichées spontanément

**Décision.** Les limites connues sont affichées par l'interface elle-même, sans que l'utilisateur ait à les chercher.

**Justification (P5).** Ces faits — déséquilibre de couverture, questions mono-formation, échantillon auto-sélectionné, reformulation assistée par modèle de langage, documents de 2024 — seront découverts. La seule question est de savoir s'ils le seront par nous, en évidence, ou par un tiers, en accusation. Un défaut annoncé par l'instrument devient une caractéristique documentée ; le même défaut révélé par un opposant devient une preuve de duplicité. Les données étant publiques, aucune autre stratégie n'est disponible.

**Conséquences.** Le composant **Portée** n'est jamais fermable, jamais repliable, jamais affiché une seule fois par utilisateur : le rendre dissimulable optimiserait la lecture d'un résultat en supprimant sa qualification, ce qui est un dark pattern.

**Impact PR.** PR-11, PR-12, PR-13.

---

## DP-14 — Ordre des questions aléatoire

**Décision.** Les questions sont présentées dans un ordre aléatoire.

**Objectifs déclarés.** Réduire les biais introduits par les abandons en cours de questionnaire ; éviter que certaines questions soient systématiquement sous-représentées.

**Conséquences.**
1. **Le regroupement thématique disparaît comme structure d'interface.** Les questions sont aujourd'hui ordonnées par thème dans le fichier (economy ×5, social ×5, …). Une recommandation antérieure d'ajouter des titres de section par thème est **caduque** : elle ne doit pas être réintroduite.
2. Le repère de position (« n / 30 ») doit être **recalculé après tirage**.
3. L'ordre tiré doit être **persisté avec le brouillon** (DT-09), faute de quoi une restauration reconstitue un questionnaire différent de celui affiché.
4. Une inférence de courbe d'abandon à partir des compteurs par question, envisagée à un stade antérieur de l'analyse, **n'est plus possible** : c'est l'effet recherché, pas un dommage collatéral.
5. La décision **doit être documentée en méthodologie** (exigence explicite).
6. L'ordre est tiré **dans le navigateur** et n'est pas enregistré ; l'interface doit le dire (P1, P2).

**Alternatives rejetées.** Ordre fixe : conserve la comparabilité exacte des agrégats et la reproductibilité de la séquence ; rejeté au profit de la réduction des effets d'ordre et de la sous-représentation des dernières questions.

**Impact PR.** PR-07, PR-08, PR-13. Rend caduque toute PR de sectionnement thématique.

---

## DP-15 — Agrégats maintenus sur la page de résultats, qualifiés

**Décision.** Les statistiques agrégées restent sur la page de résultats. Elles précisent **toujours** : la taille de l'échantillon, son caractère auto-sélectionné, et qu'il ne s'agit pas d'un sondage représentatif.

**Contexte.** L'analyse avait relevé que cette section constitue une forme de comparaison sociale, listée parmi les patrons à refuser, et proposé de la déplacer vers une page de données publiques ou de la supprimer.

**Justification retenue.** La décision est de **maintenir** la section en la qualifiant. La qualification obligatoire répond à l'objection : présentée comme un échantillon et non comme une norme, la donnée informe sans normaliser (P7).

**Conséquences.** Un seuil d'effectif existe, sous lequel seuls les effectifs bruts sont affichés, **sans pourcentage** — un pourcentage sur un effectif faible est une précision fictive (P4). Trois états distincts sont requis : service absent, service injoignable, effectif nul (P8).

## Seuil de pourcentage arrêté — définitif

> **Un pourcentage n'est affiché que si la proposition a reçu au moins 100 réponses enregistrées.**
> En deçà, seuls les **effectifs bruts** de chaque modalité sont affichés, avec l'effectif total.

L'effectif est celui d'**une proposition**, soit la somme du tableau renvoyé par `GET /counts` pour
cette question. C'est un nombre de **réponses**, jamais de personnes (DT-11) : le seuil s'applique
proposition par proposition, et deux propositions de la même page peuvent donc être affichées
différemment.

**D'où vient ce seuil.** Il est **dérivé, non choisi**. Les pourcentages sont affichés arrondis à
l'unité, ce qui annonce une précision d'**un point**. La granularité réelle d'un effectif `n` est de
`1/n` : une réponse supplémentaire déplace la valeur d'au moins `100/n` points. Afficher un
pourcentage n'est honnête que si la granularité de la donnée est au moins aussi fine que la précision
annoncée :

```
100 / n ≤ 1   ⟺   n ≥ 100
```

**100 est donc le point exact où la précision affichée cesse d'excéder la précision réelle.** En
dessous, « 43 % » annonce une précision d'un point là où la donnée n'en offre parfois que quatorze
(n = 7) : c'est la définition même de la précision fictive que P4 interdit.

**Ce que le seuil ne fait pas.** Il **ne masque aucune information** : sous 100 réponses, la
distribution complète reste affichée en effectifs bruts, avec l'effectif total et la qualification
obligatoire de l'échantillon. Seule la mise en forme qui suggère une précision inexistante est
retirée. C'est ce qui distingue ce seuil d'une dissimulation.

**Conséquences assumées.**

1. **Au lancement, aucune proposition n'atteindra 100 réponses** : la section affichera longtemps des
   effectifs bruts. C'est l'état honnête d'un service qui vient d'ouvrir, et il ne doit pas être
   contourné en abaissant le seuil.
2. Les propositions franchiront le seuil **indépendamment les unes des autres**. Une page mêlant
   effectifs bruts et pourcentages est un affichage correct, pas une incohérence.
3. Le seuil ne dépend d'aucune hypothèse de représentativité : l'échantillon reste auto-sélectionné,
   ce que la qualification obligatoire continue d'énoncer quel que soit l'effectif.

**Alternatives rejetées.**
- **Page publique de données séparée du résultat personnel**, et **suppression pure et simple** de la
  section : écartées lors de la prise de DP-15 elle-même.
- **Un seuil bas (20 ou 30)** : rejeté. À n = 20, une réponse vaut 5 points ; afficher « 45 % »
  annonce alors une précision vingt fois supérieure à la réalité. Le seuil aurait été une préférence
  déguisée en règle.
- **Aucun seuil, avec une mention « effectif faible »** : rejeté par le même raisonnement que DP-10 —
  une mise en garde ne bat jamais un grand nombre affiché.
- **Un seuil exprimé en nombre de participants** : impossible, ce nombre est structurellement
  inconnaissable (DP-03, DT-11).

**Emplacement dans le code.** Le seuil vit dans `web/src/lib/score.js`, **à un seul endroit**, aux
côtés de la règle de confiance de DP-11, exporté pour que PR-13 le lise sans le recopier.

**Impact PR.** PR-12 (implémentation), PR-13 (publication).

---

## DP-16 — Consentement opt-out, avec exposition littérale de ce qui est envoyé

**Décision.** L'utilisateur doit comprendre très précisément ce qui est envoyé, ce qui ne l'est pas, et pourquoi cette architecture protège sa vie privée. **Sans jargon juridique.**

**Justification.** La forme la plus honnête d'un consentement n'est pas une explication mais une **exposition** : montrer littéralement ce qui partira, avant que cela parte. Un consentement adossé à l'observation de la donnée elle-même n'est plus une promesse (P1). Par ailleurs, sur-insister sur la vie privée la rend suspecte : une occurrence, au moment actionnable, plus le détail complet en méthodologie.

**Conséquences.**
- La case sort de la barre flottante et rejoint un bloc de fin en flux normal, avec son explication **attenante**.
- La barre flottante est réduite à **deux éléments** : décompte et action.
- Le résidu non maîtrisé (adresse IP vue par le serveur) doit être énoncé, conformément à P2. Il est aujourd'hui signalé dans un commentaire de `index.astro:99-103`.
- Aucun terme juridique : ni « traitement », ni « responsable de traitement », ni « base légale », ni renvoi à un article de règlement.

**Impact PR.** PR-09.

---

## DP-17 — Rôle du modèle de langage documenté hors questionnaire

**Décision.** Le rôle du modèle de langage est documenté dans la méthodologie et dans la documentation détaillée des résultats. Il **ne doit pas détourner l'attention pendant le questionnaire**.

**Quatre faits obligatoires, dans cet ordre :**
1. génération de brouillons **hors ligne** ;
2. **relecture humaine obligatoire** avant toute intégration ;
3. **aucune IA pendant l'exécution** du site ;
4. **vérification automatique des citations**.

**Justification de l'ordre.** Le fait le plus inquiétant est énoncé en premier, ce qui rend la suite crédible. L'ordre inverse ressemblerait à une justification.

**Justification de l'existence.** Ce fait est publié dans le dépôt. S'il n'est pas dans l'interface, le projet pratique une honnêteté à deux étages : franche envers ceux qui lisent le code, silencieuse envers les autres (P10).

**Conséquences.** L'encart méthodologique ne comporte aucune formule d'atténuation (« ne vous inquiétez pas », « comme la plupart des outils »).

**Alternatives rejetées.** Mention en évidence près des questions : maximalement honnête mais exposant à un rejet réflexe qui écraserait la nuance, **et interdite par la décision** ; confinement exclusif au dépôt : rejeté par P10.

**Impact PR.** PR-13.

---

## DP-18 — L'anglais devient une aide à la lecture

**Décision.** Les citations officielles restent dans leur langue d'origine. L'utilisateur doit toujours pouvoir distinguer **notre traduction**, **notre reformulation** et **le texte officiel**.

**Contexte.** Un utilisateur anglophone répondait jusqu'ici à la traduction anglaise de notre reformulation française d'un document français : deux couches éditoriales le séparaient de la source, et la citation qui lui est montrée à la révélation est en français, donc invérifiable pour lui.

**Conséquences dérivées.**
- Les **énoncés** restent affichés en français, avec la traduction anglaise **adjacente**, marquée, de corps réduit. Jamais en substitution.
- Les **citations** ne sont jamais traduites en substitution ; une traduction peut être adjointe.
- Le **chrome** (libellés de contrôle, navigation) est intégralement traduit.
- **Attribut de langue par nœud obligatoire** : sans lui, la synthèse vocale prononce du français avec des règles anglaises et le contenu devient inintelligible. Ce n'est pas une amélioration, c'est la condition d'utilisabilité de la version anglaise.

**Coût assumé.** Les pages sont plus hautes en anglais, du fait de la traduction adjacente des **énoncés**. En revanche, **les libellés de l'échelle sont du chrome** : ils sont traduits, jamais doublés, et leur jeu unique (DP-26) est déjà dimensionné pour 320 px dans les deux langues. La densité de la grille de réponse n'augmente donc pas en interface anglaise.

**Alternatives rejetées.** Maintenir la version anglaise complète (chaîne de fidélité plus longue, citation invérifiable) ; retirer l'anglais (portée réduite).

**Impact PR.** PR-14, PR-06 (contrainte de largeur).

---

## DP-19 — Résultat calculé quel que soit le nombre de réponses

**Décision.** Le résultat est calculé quel que soit le nombre de réponses. L'interface doit **immédiatement** rendre visible la quantité de données réellement comparées, afin que l'utilisateur juge lui-même de la solidité du résultat.

**Justification.** Fixer un seuil minimal reviendrait à décider à la place de l'utilisateur que sa passation est insuffisante, et à lui refuser un résultat après un effort réel. Rendre la base visible au premier rang laisse « 1 proposition comparée » se disqualifier tout seul, sans que nous ayons eu à en juger.

**Conséquences.** Le comportement actuel — un message si aucune réponse n'est donnée — reste, mais doit proposer une action plutôt que constater. Aucun seuil minimal de calcul n'est introduit.

**Impact PR.** PR-11.

---

## DP-20 — Pas de barre de progression

**Décision.** Aucune barre de progression graphique. Le décompte textuel suffit.

**Justification (P9).** Une barre de progression n'informe pas mieux qu'un décompte « 12 / 30 » : elle existe pour créer une tension d'achèvement. Le test décisif — *si cet élément était retiré, l'utilisateur serait-il moins informé, ou seulement moins susceptible d'aller au bout ?* — la classe dans la seconde catégorie.

**Historique.** Elle avait été proposée « fine et non animée » à un stade antérieur de l'analyse, puis abandonnée. Elle est désormais **interdite**, sans arbitrage possible.

**Impact PR.** Aucune. Interdiction opposable en revue.

---

## DP-21 — Animations limitées à une liste fermée

**Décision.** Deux animations autorisées, et aucune autre : transition de couleur sur survol et appui d'un contrôle (≤ 120 ms) ; ouverture et fermeture **native** d'un bloc repliable.

**Critère.** Une animation est autorisée si et seulement si **sa suppression prive l'utilisateur d'une information**. Si sa suppression ne fait que rendre l'interface moins agréable, elle est interdite.

**Conséquences.** Toute animation autorisée est supprimée sous préférence de mouvement réduit, et l'interface doit rester **strictement équivalente en information** sans elle. Aucune animation ne peut donc être le seul véhicule d'un changement d'état.

**Interdits nommément.** Apparition et fondu, progression, animations liées au défilement, mise en scène de la révélation, squelette animé, défilement automatique, mouvement d'attraction.

**Impact PR.** PR-03 (borne de durée testée), toutes les autres (interdiction).

---

## DP-22 — Interface achromatique : aucune couleur d'accent

**Décision.** L'interface n'utilise **aucune teinte**. Aucune information n'est portée par la couleur.

**Justification, par ordre de force.**
1. **Neutralité structurelle.** En France, presque toute teinte est appropriée par une formation ou un courant : bleu, rouge, vert, orange, violet. Une palette neutre choisie avec soin resterait une palette dont il faudrait défendre chaque valeur. L'absence de teinte rend la faute **impossible plutôt qu'improbable** — la même logique que l'aveuglement structurel (DP-01).
2. **Accessibilité par construction.** WCAG 1.4.1 devient inviolable au lieu d'être surveillé.
3. **Résistance dans le temps.** Une palette est le premier élément qu'un contributeur veut rafraîchir ; une absence de palette n'offre pas de prise.

**Conséquences.**
- L'anneau de focus devient **double et achromatique** — ce qui est en outre plus robuste : un anneau de teinte unique échoue toujours sur au moins un fond.
- Les neutres restent **légèrement chauds** en clair : cela évoque un support imprimé sans introduire de code couleur.
- Aucun jeton n'est nommé d'après une signification (`success`, `warning`, `danger`, `primary`) : on ne peut pas dériver un code couleur d'un vocabulaire qui n'en contient pas.
- Les marques de données ont un **remplissage uniforme** : une échelle de valeurs de gris serait lue comme « plus » ou « pire ».

**Seuls écarts admis.** Les couleurs imposées par le système en mode contraste forcé, et les couleurs de documents cités si un fac-similé était un jour affiché — c'est-à-dire des couleurs dont nous ne sommes pas l'auteur.

**Impact PR.** PR-03 (test de jetons), toutes les autres (interdiction).

---

## DP-23 — Métadonnées de partage reléguées, hors des 14 PR

**Décision.** Les métadonnées de partage (`og:*`) sont admissibles pour partager **l'outil**, jamais un résultat, sans slogan, sans chiffre d'usage et sans indice de formation. **Aucune des 14 PR ne les traite.**

**Justification.** C'est l'élément le plus proche du marketing de toute la liste. Le partage d'un **résultat** est en revanche définitivement interdit : il transformerait un exercice d'introspection en signal d'appartenance publié, c'est-à-dire en restauration du biais que l'outil sert à supprimer.

**Impact PR.** Aucune. À traiter hors chantier si le besoin se confirme.

---

## DP-24 — Pas de commutateur de thème manuel

**Décision.** Le thème suit `prefers-color-scheme`. Aucun commutateur.

**Justification.** Un commutateur est une préférence à conserver, donc un état à stocker sur l'appareil de l'utilisateur, pour un gain nul.

**Impact PR.** PR-03.

---

## DP-25 — Aucune pré-sélection, aucune avance automatique

**Décision.** Aucune réponse n'est pré-sélectionnée. L'interface n'avance pas automatiquement après une sélection. L'option de non-réponse est séparée du groupe des cinq positions et n'est jamais cochée par défaut.

**Contexte.** `index.astro:41` coche aujourd'hui l'option « Passer » sur les 30 questions, avec le style d'état sélectionné (bordure d'accent, fond teinté, graisse 600).

**Justification.** Une réponse pré-sélectionnée revient à ce que **l'outil réponde à la place de l'utilisateur sur un instrument politique**. Trois effets se cumulent aujourd'hui : le formulaire est complet dès l'ouverture (aucune tension d'achèvement) ; l'utilisateur voit 30 options cochées pendant que le décompte affiche « 0 réponse », soit deux éléments de l'interface qui se contredisent à l'écran ; « Passer » occupe le même rang visuel qu'un choix considéré, ce qui banalise l'abstention.

**Note.** « Neutre » et « Passer » sont traités à l'identique par `score.js:16`. La distinction n'a d'effet que sur les compteurs publics : elle reste légitime (pas d'avis ≠ position équilibrée) mais doit être documentée en méthodologie plutôt qu'expliquée à chaque question.

**Impact PR.** PR-04, PR-06.

---

## DP-26 — Libellés de l'échelle de réponse : un jeu unique, à toutes les largeurs

**Décision.** L'échelle affiche **un seul jeu de libellés, identique à toutes les largeurs de viewport**,
dimensionné pour tenir à 320 px. Il n'existe **pas** de forme longue au large et de forme abrégée à
l'étroit.

| Position | Libellé **affiché** FR | Libellé **affiché** EN | Nom accessible (FR / EN) |
|---|---|---|---|
| 1 | « Pas du tout » | « Not at all » | « Pas du tout d'accord » / « Strongly disagree » |
| 2 | « Plutôt pas » | « Rather not » | « Plutôt pas d'accord » / « Somewhat disagree » |
| 3 | « Neutre » | « Neutral » | « Neutre » / « Neutral » |
| 4 | « Plutôt oui » | « Rather yes » | « Plutôt d'accord » / « Somewhat agree » |
| 5 | « Tout à fait » | « Fully agree » | « Tout à fait d'accord » / « Strongly agree » |

**Le nom accessible reste la formulation complète**, dans les deux langues, conformément au système
d'interface. C'est lui que restitue un lecteur d'écran, et c'est lui que publie la méthodologie.

**Justification — pourquoi un jeu unique, et non deux formes selon la largeur.**

C'est **INV-18** qui tranche, pas la typographie. Un jeu de libellés qui change avec la largeur du
viewport présente **des ancres différentes selon l'appareil** : un utilisateur sur téléphone et un
utilisateur sur ordinateur ne répondraient pas au même instrument. INV-18 n'admet qu'une seule
exception documentée — le tirage d'ordre de DP-14 — et la largeur d'écran n'en fait pas partie.
Une variation d'ancres entre sujets est une variation de mesure entre sujets.

**Justification — pourquoi ces libellés-là.**

1. **Contrainte dimensionnante mesurée.** À 320 px, avec un remplissage de page de 16 px de chaque
   côté et quatre intervalles de 4 px, chaque colonne dispose d'environ **54 px**. À 0.8125rem
   (13 px, la plus petite taille de l'échelle typographique), cela laisse environ **8 caractères par
   ligne** avant remplissage de cellule. La cible retenue est **7 caractères maximum par mot**, ce
   qui conserve une marge sur toutes les piles de polices système.
2. **Les formulations complètes ne tiennent pas.** « Pas du tout d'accord » exige un mot de 8
   caractères (« d'accord ») et une première ligne de 11 (« Pas du tout ») : environ 68 px, soit
   au-delà de la colonne. Le constat vaut pour les quatre libellés non neutres.
3. **Symétrie des paires.** Les positions 2 et 4 forment une paire (« Plutôt pas » / « Plutôt oui »),
   les positions 1 et 5 une autre (« Pas du tout » / « Tout à fait »). L'axe se lit **sans lire les
   mots en entier**, ce qui est précisément ce que le repli détruisait avant PR-06.
4. **Désambiguïsation.** Une abréviation par troncature — « Plutôt pas » face à « Plutôt » — aurait
   conservé une fidélité littérale au prix d'une ambiguïté sur la position 4. Un clic erroné dû à un
   libellé ambigu déforme la distribution des réponses : c'est un **défaut de mesure**, la catégorie
   de défaut que PR-06 existe pour éliminer. La fidélité littérale d'un affordance d'affichage cède
   devant l'exactitude de la mesure, d'autant que le nom accessible et la méthodologie conservent la
   formulation intégrale.
5. **Compensation de l'écart sémantique.** L'écart entre « Plutôt oui » et « Plutôt d'accord » est
   compensé par le rappel des pôles de l'axe **en toutes lettres**, déjà exigé par PR-06 à intervalle
   régulier : la formulation complète est donc présente à l'écran quoi qu'il arrive.

**Conséquences assumées.**

1. Les libellés affichés ne sont **pas** la reprise littérale des `CHOICE_LABELS` actuels. Les
   formulations complètes ne disparaissent pas : elles deviennent les **noms accessibles** et sont
   publiées en méthodologie (PR-13), avec les deux formes en regard.
2. **Aucun point de rupture n'est introduit** pour l'échelle. Le corpus normatif n'en déclarait aucun ;
   cette décision n'en crée pas.
3. L'anglais ne double pas les libellés : ce sont des **libellés de contrôle**, donc du chrome, que
   DP-18 fait traduire intégralement plutôt qu'accompagner d'une traduction adjacente. La contrainte
   de largeur en interface anglaise porte donc sur les seuls libellés anglais.

**Alternatives rejetées.**

- **Deux formes selon la largeur** (complète au large, abrégée à l'étroit) : rejetée par INV-18 —
  variation d'ancres entre utilisateurs. C'est l'alternative qui semblait la plus naturelle et c'est
  celle qui pose le problème le plus grave.
- **Formulations complètes partout, repliées sur trois lignes** : rejetée, elle exige un mot de 8
  caractères dans une colonne de 54 px moins le remplissage de cellule ; la marge est nulle ou
  négative selon la pile de polices système, et une décision ne peut pas reposer sur une mesure
  marginale.
- **Chiffres 1 à 5 avec légende** : compacts et ordonnés, mais ils transforment une échelle
  sémantique en échelle numérique, invitent à la moyenne arithmétique — précision fictive interdite
  par P4 — et se lisent comme une note. Les règles de rédaction du projet privilégient les mots sur
  les codes.
- **Troncature littérale** (« Plutôt… » en position 4) : rejetée pour l'ambiguïté décrite ci-dessus.
- **Réduction de la taille de police sous 0.8125rem** : impossible, c'est le plus petit échelon de
  l'échelle typographique et l'échelle n'admet aucune valeur hors de ses six pas.

**Échappatoire documentée, à n'utiliser qu'en cas de débordement mesuré.** Si un mot déborde sur une
pile de polices système lors du protocole des neuf largeurs, la correction autorisée est de **réduire
le remplissage de page de 16 px à 8 px sous 320 px** — deux valeurs de l'échelle d'espacement
autorisée — et **non** de modifier les libellés, qui sont normatifs.

**Impact PR.** PR-06 (implémentation et protocole), PR-13 (publication des deux formes), PR-14
(traduction du chrome ; aucune adaptation de largeur n'est requise puisque les libellés anglais sont
déjà dimensionnés).

---

## DP-27 — En-tête du questionnaire : contenu, ordre et cap

**Décision.** Le questionnaire porte un **en-tête unique**, en tête de page, composé d'au plus **cinq
énoncés courts**, dans cet ordre :

1. **Ce que c'est et ce qui est attendu** — la nature de l'instrument et la tâche.
2. **La matière et sa datation** — nombre de propositions, nombre de formations, et le fait que les
   documents utilisés ont été **publiés en 2024** alors que le questionnaire vise 2027.
3. **Le statut éditorial des énoncés** — ce sont **nos reformulations**, pas des citations.
4. **Le déroulé** — l'ordre des questions est **tiré au hasard dans le navigateur et n'est pas
   enregistré** ; aucune formation n'est nommée avant la dernière réponse.
5. **La condition technique** — le questionnaire **nécessite JavaScript** pour enregistrer et calculer.

Plus **un lien vers la page de méthodologie**, et rien d'autre.

**Cap vérifiable.** Un seul bloc ; **cinq énoncés au maximum** ; **120 caractères au maximum par
énoncé** ; aucun titre de niveau inférieur ; aucune illustration ; **aucun bouton d'action** autre que
le lien vers la méthodologie.

**D'où vient le cap de 120 caractères.** C'est la **longueur du plus long énoncé de question du
corpus** (`MIGRATION.md` §8 : maximum 120 caractères en français). Aucune phrase d'en-tête ne doit
être plus longue que la plus longue chose que l'utilisateur doit de toute façon lire. Le cap est donc
**dérivé d'une mesure du corpus**, pas choisi, et il est vérifiable par comptage — contrairement à un
cap exprimé en lignes, qui dépend de la largeur du viewport et n'est donc pas vérifiable.

**Justification du contenu.** Les cinq énoncés ne sont pas une sélection éditoriale : ce sont
exactement les éléments que le budget d'attention à 10 secondes du système d'interface rend
obligatoires, plus les deux annonces que PR-07 doit de toute façon écrire. La datation du corpus est
l'application la plus rentable de **P5** — c'est l'information la plus susceptible de faire crier à
la tromperie si elle est découverte après coup — et le statut éditorial est l'application directe de
**P3**, la couche de reformulation étant le seul endroit du dispositif où un biais peut s'introduire
sans laisser de trace dans une empreinte.

**Justification de l'attribution à PR-07.** PR-07 est **la seule PR qui doit déjà écrire du contenu
d'en-tête** : DP-14 lui impose d'annoncer le tirage et son caractère non enregistré, et l'exigence de
JavaScript. Toute autre attribution — PR-04, PR-13, ou une PR dédiée — impose **deux passes
d'écriture et deux relectures sur le même bloc de texte**, la seconde restructurant ce que la première
vient d'écrire.

**Conséquences assumées.**

1. **PR-07 mêle une modification mécanique** (la permutation) **et une modification éditoriale**
   (l'en-tête). C'est admis parce que leurs critères de validation sont distincts et cumulables : la
   permutation se valide par M1 et le protocole de première peinture, l'en-tête par relecture et
   comptage de caractères. Le document de PR-07 les traite séparément.
2. L'en-tête reste **au-dessus** de la première question et n'est ni replié, ni fermable : les cinq
   énoncés relèvent du niveau 2 de la hiérarchie, qui ne peut jamais être supprimé pour alléger.
3. **Aucune landing n'est créée** (DP-07) : le cap structurel — cinq énoncés, aucun bouton d'action,
   aucune illustration — est ce qui empêche l'en-tête de redevenir une page de conversion par
   accumulation.

**Alternatives rejetées.**

- **PR-04 élargie** : PR-04 est définie comme un lot de « correctifs sans décision » ; y verser un
  contenu éditorial contredirait sa nature et l'obligerait à être relue comme un texte. De plus,
  PR-07 réécrirait ensuite deux de ses cinq énoncés.
- **PR-13** : la méthodologie est une destination **secondaire**. Un fait qui doit précéder la
  passation ne peut pas vivre uniquement dans une page qu'on atteint en un clic depuis le
  questionnaire.
- **Une PR-15 dédiée** : séparation la plus propre en théorie, mais elle touche le même fichier que
  PR-07, se sérialise donc avec elle, et arrive après que PR-07 a écrit deux énoncés qu'elle
  restructure immédiatement.
- **Un cap exprimé en lignes** (« trois lignes maximum ») : rejeté, une ligne n'est pas une unité
  vérifiable — elle dépend de la largeur du viewport et de la taille de police de l'utilisateur.

**Impact PR.** PR-07 (implémentation), PR-04 (n'a plus à s'en préoccuper), PR-13 (la méthodologie
développe ces cinq points, elle ne les remplace pas).

---

## DP-28 — Bloc de provenance en tête de la page de résultats

**Décision.** La page de résultats porte, **en tête, avant les résultats par formation**, un bloc
listant les documents sources du corpus : **une ligne par document**, portant son **titre exact**, sa
**date de publication**, son **empreinte SHA-256 tronquée et copiable en entier**, et un **lien vers le
document**. Le bloc est rendu au **registre appareil** (0.8125rem), n'est ni repliable ni fermable.

**Justification.** La citation sourcée est ce qui distingue Civis d'un quiz, et elle est aujourd'hui
l'élément le mieux caché du produit. Le bloc établit, avant tout chiffre, **sur quoi reposent les
chiffres qui suivent** — application directe de **P4** (la base voyage avec la mesure) et de **P6**
(l'instrument est daté et attribuable).

**Justification du registre appareil, et non du niveau 1.** Placé en corps de lecture, un bloc de
quatre documents avec empreintes formerait un mur avant la révélation. Le système d'interface classe
la provenance au **niveau 2 — appareil** : structurellement lié à la matière, jamais séparable d'elle,
mais plus petit et moins appuyé. Une ligne par document, au registre appareil, occupe quatre lignes et
non un écran.

**Justification de l'attribution à PR-11.**

1. **PR-13 ne peut pas l'héberger** : le bloc vit sur la page de résultats, or `results.astro` figure
   dans la liste des fichiers interdits de PR-13. L'y attribuer imposerait de démonter cette
   interdiction, qui protège le périmètre de la PR la plus rédactionnelle du chantier.
2. **PR-10 ne peut pas l'héberger** : son critère est une sortie inchangée ; ajouter un bloc la
   ferait échouer.
3. **PR-12 ne peut pas l'héberger** : elle ne touche que la section des agrégats.
4. **PR-11 est la dernière PR à restructurer cette page**, et elle introduit déjà la **couverture**,
   qui est également une métadonnée de corpus et non une propriété du résultat personnel. Le bloc de
   provenance appartient à la même famille : il ne dilue pas l'objet de PR-11, il le complète.

**Conséquences assumées.**

1. PR-11 grossit d'un bloc borné : quatre documents, quatre champs. Les données sont déjà aplaties au
   build par le frontmatter existant, et le composant **Source** créé par PR-10 est réutilisé — aucune
   nouvelle abstraction.
2. Les mêmes documents apparaîtront **deux fois dans le produit** : en tête des résultats et dans la
   méthodologie. Ce n'est pas une duplication de données — les deux pages **lisent la même source**,
   jamais une copie (INV-07) — mais une duplication d'affichage, assumée : les deux pages s'adressent
   à des lecteurs différents à des moments différents.
3. Les empreintes sont lues au build depuis `content/sources/<élection>/*.sha256`, fichiers texte au
   format `<empreinte>  <url>`, comme le fait déjà PR-13.

**Alternatives rejetées.**

- **PR-13** : impossible sans violer sa liste de fichiers interdits, voir ci-dessus.
- **Une PR dédiée** : elle toucherait `results.astro`, donc se sérialiserait avec PR-10, PR-11 et
  PR-12 sans gain de parallélisme, pour un contenu de quatre lignes.
- **Placer le bloc en pied de page de résultats** : rejeté, P4 impose que la base précède ou
  accompagne la mesure, jamais qu'elle la suive.
- **Ne pas afficher les empreintes** (seulement titre, date et lien) : rejeté, l'empreinte est ce qui
  rend la vérification possible sans nous croire sur parole (P1).

**Impact PR.** PR-11 (implémentation), PR-10 (crée le composant Source réutilisé), PR-13 (développe
les mêmes documents pour un autre lecteur, sans recopier).

---

# Décisions techniques

## DT-01 — Aucune nouvelle dépendance npm

**Décision.** Le chantier n'ajoute aucune dépendance. Le dépôt en compte une : `astro@^5.6.1`.

**Justification.** Mainteneur unique. Tous les contrôles proposés tiennent dans `node --test`, déjà présent et sans configuration.

**Alternatives rejetées.** `stylelint` pour la police des jetons ; un pilote de navigateur pour les tests d'interface ; une bibliothèque d'audit d'accessibilité. Chacun résoudrait un problème réel au prix d'un coût de maintenance supérieur au gain.

**Impact PR.** Toutes. Opposable en revue.

---

## DT-02 — Tests via `node --test` ; vérification navigateur manuelle et normée

**Décision.** Aucun test de navigateur automatisé. La vérification manuelle est **normée** (M1–M8) et référencée par identifiant dans chaque PR.

**Justification.** Introduire un pilote de navigateur pour un dépôt de 600 lignes maintenu par une personne coûterait plus en maintenance qu'il ne rapporterait.

**Conséquence assumée.** Tout ce qui relève du rendu, du clavier, du lecteur d'écran, du contraste forcé et des largeurs n'est pas testé automatiquement.

**Impact PR.** Toutes.

---

## DT-03 — Jetons dans un fichier CSS dédié

**Décision.** Les jetons vivent dans **un fichier dédié**, importé par `styles.css`, contenant exclusivement des déclarations de variables : couleur, taille, interlignage, espacement, épaisseur, rayon, mesure, durée. Aucune règle, aucun sélecteur autre que `:root` et le bloc de préférence de thème.

**Justification du fichier séparé.** Raison de revue : plusieurs questions de la checklist portent sur les valeurs. Un fichier dédié rend la réponse immédiate — *cette PR modifie-t-elle le fichier de jetons ?* Si oui, elle relève d'une modification du système d'interface et non d'un changement de fonctionnalité.

**Alternatives rejetées.** Configuration JavaScript exportée vers CSS : introduirait une étape de génération, un artefact à synchroniser et une indirection sans contrepartie sur un dépôt sans préprocesseur. Les propriétés personnalisées CSS se cascadent naturellement dans les deux thèmes et sont lisibles dans l'inspecteur du navigateur — ce qui sert la vérifiabilité.

**Périmètre exclu.** Les points de rupture responsive (le système n'en définit qu'un) et les valeurs propres à un composant unique. Jetonniser ce qui n'apparaît qu'une fois produit une indirection moins lisible que la valeur qu'elle remplace.

**Impact PR.** PR-03.

---

## DT-04 — Tests automatisés de jetons et de contraste

**Décision.** Deux tests distincts, exécutés par `npm test`.

**Test de jetons.** Échoue sur : toute valeur colorimétrique littérale hors du fichier de jetons ; toute longueur hors échelle (avec une liste d'exceptions explicite et courte : zéro, épaisseurs de bordure, pourcentages de mise en page) ; toute taille de police littérale ; toute durée supérieure à la borne ; **tout attribut `style=` dans un fichier de composant ou de page** ; toute règle réintroduisant une propriété de teinte.

**Test de contraste.** Lit les valeurs de jetons, calcule les ratios, échoue sous les seuils. Distinct du précédent : il rend impossible l'introduction d'une valeur conforme au **format** mais non conforme au **niveau d'accessibilité** — le cas exact du défaut actuel, où `--line` respecte parfaitement le système de jetons tout en échouant à 1,37:1.

**Justification.** C'est le pendant, côté interface, de ce que `pipeline.check` fait côté contenu : la contrainte est vérifiée par une machine plutôt qu'affirmée dans une documentation. Seule forme d'application qui survit à plusieurs années et à plusieurs contributeurs.

**Conséquence de gouvernance.** La liste d'exceptions vit dans le test lui-même. L'allonger est visible en revue. Une liste qui s'allonge de PR en PR est le symptôme d'un système d'espacement inadapté : c'est le système qu'il faut réviser, explicitement.

**Exceptions temporaires pour les attributs `style=` inline — règle de scission.** Le dépôt compte huit attributs `style=` au moment de PR-03 : **trois dans `index.astro`** (lignes 50, 55, 63) et **cinq dans `results.astro`** (lignes 124, 127, 151, 176, 180). PR-03 ne peut pas les supprimer, ces deux fichiers lui étant interdits. Le test de jetons doit donc porter **deux exceptions nommées et séparées**, non une seule :

| Exception | Couvre | Retirée par |
|---|---|---|
| `inline-styles-questionnaire` | Les 3 occurrences de `index.astro` | **PR-04** |
| `inline-styles-resultats` | Les 5 occurrences de `results.astro` | **PR-10** |

**Motif de la scission.** Une exception unique retirée par PR-04 laisserait le test rouge et la CI bloquée jusqu'à PR-10, six PR plus loin et parallélisable. Chaque exception porte dans le test un commentaire nommant la PR qui la retire et la date de sa création.

**Impact PR.** PR-03 (création des deux exceptions), PR-04 (retrait de la première), PR-10 (retrait de la seconde). Le test doit appartenir à PR-03 ou à aucune : écrit après coup, il devrait intégrer les écarts existants dans ses exceptions et perdrait sa fonction.

---

## DT-05 — Contrôle d'aveuglement sur la sortie compilée

**Décision.** Un script parcourt, **après `npm run build`**, la page de questionnaire compilée et **tous les avoirs JavaScript qu'elle référence**, et échoue si l'un d'eux contient un identifiant, un nom ou un sigle de formation lu depuis `content/programs/`.

**Justification.** Le contrôle porte sur la **sortie**, pas sur la source : c'est la seule position qui résiste à un import ajouté par inadvertance. Un contrôle sur les imports de `index.astro` serait contournable par un import transitif.

**Contrainte de chaîne.** `npm test` s'exécute **avant** `npm run build` dans le workflow : le contrôle doit donc être une étape distincte, postérieure au build.

**Impact PR.** PR-01. Doit passer sur toutes les PR ultérieures.

---

## DT-06 — Extraction des composants avant les PR qui modifient le questionnaire

**Décision.** PR-05 crée `web/src/components/` et déplace le balisage, **sans aucun changement de sortie**.

**Justification.** Cinq PR identifiées — 06, 07, 08, 09, 14 — doivent modifier le questionnaire. Sans extraction préalable, elles se disputent le même fichier de 117 lignes. Ce n'est pas une abstraction spéculative : elle est justifiée par des modifications **déjà planifiées et nommées**.

**Garde-fou.** Chaque composant créé doit correspondre à une PR ultérieure identifiée. Créer un composant utilisé une seule fois et jamais modifié serait une abstraction spéculative, contraire à la contrainte de maintenabilité.

**Périmètre de PR-05 : le questionnaire uniquement.** PR-05 crée **Question** et **Échelle de réponse**, et ne touche pas `results.astro`. Raison : le balisage des résultats n'y existe pas comme balisage mais comme **gabarits de chaînes JavaScript** assemblés par `innerHTML` à l'exécution. L'extraire en composants Astro signifie le rendre au build, donc changer la sortie compilée — ce que le critère octet à octet de PR-05 (DT-20) interdit. Les composants **Citation, Source et Résultat sont créés par PR-10**, en même temps qu'elle convertit le rendu.

**Alternative rejetée.** Laisser PR-05 choisir d'extraire ou non les composants de résultats : rejetée parce que l'option est infaisable, et parce qu'une option infaisable offerte dans un document d'implémentation conduit une session à conclure que c'est le critère de validation qui est trop strict.

**Impact PR.** PR-05, PR-10.

---

## DT-07 — Résultats rendus en statique

**Décision.** Le détail des résultats est rendu au build en balisage Astro. Le script résiduel se limite à filtrer les questions sans réponse, injecter la réponse de l'utilisateur et calculer le résultat.

**Justification.** 100 % des données affichées sont connues au build. Le rendu client actuel produit : une page vide sans JS, un flash de contenu vide avec JS lent, un échappement manuel maison, et 90 lignes de HTML dans des chaînes.

**Aucun invariant n'est affecté** : le JSON des formations est **déjà** inliné dans la page de résultats (`results.astro:69-92`). Rendre le contenu en statique n'expose donc rien de plus.

**Impact PR.** PR-10.

---

## DT-08 — Permutation par déplacement DOM avant premier rendu

**Décision.** Le tirage d'ordre (DP-14) est appliqué en **déplaçant les nœuds dans le DOM**, avant le premier rendu visible.

**Alternative explicitement interdite.** Un réordonnancement visuel par propriété de mise en page (par exemple `order` sur un conteneur flex ou grid) laisserait l'ordre de tabulation inchangé et produirait une **dissociation entre parcours visuel et parcours clavier** — violation directe de WCAG 2.4.3 et de INV-17. Cette solution est celle qui vient naturellement, et elle casse silencieusement : rien à l'écran ne le révèle, seul un test au clavier le détecte. Elle doit être refusée en revue.

**Conséquence.** Une permutation appliquée après le premier rendu produit un réagencement visible ; elle doit donc intervenir avant.

**Impact PR.** PR-07.

---

## DT-09 — L'ordre tiré est persisté avec le brouillon

**Décision.** L'ordre tiré est enregistré avec les réponses, dans la **même clé `sessionStorage`** que le brouillon.

**Justification.** Sans cela, une restauration reconstitue un questionnaire **différent de celui affiché** au moment de l'abandon : les repères « n / 30 » ne correspondent plus, et l'utilisateur ne retrouve pas la question qu'il était en train de lire.

**Contrainte.** Le format doit rester compatible avec la lecture qu'en fait la page de résultats (`results.astro:100`).

**Impact PR.** PR-08. Découle de DP-09 + DP-14.

---

## DT-10 — Aucune modification de l'API

**Décision.** Les 14 PR ne touchent pas à `api/`.

**Justification.** `GET /counts` renvoie déjà `{questionId: [n0..n4]}` pour toutes les questions connues, échelle complète garantie. L'effectif exigé par DP-15 est la **somme du tableau** d'une question, calculable côté client.

**Impact PR.** PR-12.

---

## DT-11 — « Réponses par proposition », jamais « participants »

**Décision.** Tout libellé d'effectif désigne un nombre de **réponses enregistrées pour une proposition**.

**Justification.** L'architecture rend le nombre de personnes structurellement inconnaissable (DP-03). Un libellé parlant de « participants » serait **factuellement faux** et contredirait, dans les mots, l'invariant qu'il est censé illustrer.

**Impact PR.** PR-12.

---

## DT-12 — Empreintes lues au build par import brut

**Décision.** Les fichiers `content/sources/<élection>/*.sha256` sont lus au build par import brut.

**Justification.** Ce ne sont pas des fichiers JSON : leur contenu est `<empreinte>  <url>` en texte. `vite.server.fs.allow: [".."]` (`astro.config.mjs:21`) autorise déjà la lecture hors de `web/`.

**Alternative rejetée.** Recopier les empreintes dans `sources.json` : créerait une seconde copie susceptible de diverger de la source de vérité.

**Impact PR.** PR-13.

---

## DT-13 — SHA de commit et date injectés au build ; build local identifié comme tel

**Décision.** Le workflow injecte le SHA de commit et la date de construction. En développement local, l'appareil de version annonce un **build local**.

**Justification.** Afficher une valeur inventée violerait P1 **sur le composant censé le porter**. C'est le seul endroit du produit où une valeur factice serait une contradiction performative.

**Impact PR.** PR-02.

---

## DT-14 — Identifiant de page de la méthodologie : `method`, identique dans les deux langues

**Décision.** La page de méthodologie porte l'identifiant **`method`**, **identique en français et en
anglais**. Les routes générées sont `/<base>/fr/method/` et `/<base>/en/method/`, et `Base.astro`
reçoit `page="method"` sans aucune modification de sa logique.

**Justification par le précédent du dépôt.** Le choix du mot n'est pas une préférence : **la page de
résultats existante porte déjà le slug anglais `results`** — `Base.astro` reçoit `page="results"`, et
`index.astro` construit `href(\`${lang}/results/\`)`. Le dépôt a donc déjà tranché la question du
registre linguistique des slugs, dans le sens de l'anglais. `method` prolonge ce précédent au lieu
d'ouvrir une exception.

**Justification par les décisions existantes.**

1. **INV-15** : le contenu politique est en français, le code et les identifiants en anglais. Un slug
   est un identifiant de route.
2. **DP-18** : l'anglais est une **aide à la lecture**, pas une localisation complète. Un slug
   localisé (`/fr/methode/` face à `/en/method/`) suggérerait un site anglais complet qui n'existe
   pas, et sur-promettrait ce que le produit fait.
3. **Maintenabilité** : `Base.astro:23` construit les liens de langue par `href(\`${code}/${page}\`)`
   depuis une propriété unique. Un slug localisé imposerait une table de correspondance
   langue → slug, maintenue par une seule personne, **pour une seule page**.

**Conséquences assumées.**

1. Un lecteur francophone verra une URL en anglais. C'est déjà le cas pour la page de résultats ; la
   cohérence interne prime sur l'esthétique d'une URL.
2. Aucune modification de `Base.astro` n'est nécessaire au-delà de l'ajout du lien lui-même : le
   sélecteur de langue fonctionne tel quel depuis la nouvelle page.
3. **Point de vigilance** relevé dans le dépôt : le sélecteur de langue produit `fr/results` **sans**
   barre oblique finale, tandis que `index.astro` lie vers `fr/results/` **avec**. Les deux
   fonctionnent ; la nouvelle page doit se comporter comme l'existante et ce détail ne doit pas être
   « corrigé » à l'occasion de PR-13, ce qui sortirait de son périmètre.

**Alternatives rejetées.**

- **Slug localisé par langue** (`/fr/methode/`, `/en/method/`) : rejeté pour les trois motifs
  ci-dessus — table de correspondance à maintenir, sur-promesse de localisation, et rupture avec le
  précédent `results`.
- **Slug français identique dans les deux langues** (`/fr/methode/`, `/en/methode/`) : cohérent avec
  la langue du contenu, mais **en rupture avec le précédent `results`** et avec INV-15. Retenir le
  français aurait imposé, par cohérence, de renommer `results` — un changement hors périmètre du
  chantier et sans rapport avec son objet.

**Statut.** **Décision arrêtée.** Elle remplace la recommandation antérieure, qui portait sur le
principe (identifiant identique) sans trancher le mot.

**Impact PR.** PR-13.

---

## DT-15 — PR-03 seule restructure `styles.css`

**Décision.** `web/src/styles.css` est restructuré une seule fois, par PR-03. Les PR suivantes n'y **ajoutent** que des blocs, en fin de fichier, sans réorganiser. **Le fichier n'est jamais déplacé** : il reste `web/src/styles.css`, et le fichier de jetons est créé à côté de lui, pas dans un nouveau répertoire.

**Justification.** C'est le point de conflit Git unique du chantier : le fichier est touché par PR-02, 03, 06, 09, 11, 12, 13 et 14. Le non-déplacement est une contrainte de traçabilité : toutes les listes « fichiers concernés » et « fichiers interdits » des PR-02 à PR-14 désignent ce chemin exact ; un déplacement les rendrait fausses et rendrait les interdits inopposables en revue.

**Conséquence directe sur la planification.** **PR-02 et PR-03 ne peuvent pas être ouvertes simultanément.** PR-02 ajoute des règles au fichier que PR-03 réécrit intégralement. L'ordre entre elles est libre — PR-02 ajoute en fin de fichier si PR-03 n'est pas fusionnée, et consomme les jetons si elle l'est — mais leur simultanéité produit un conflit sur la totalité du fichier, soit exactement ce que cette décision existe pour éviter.

**Impact PR.** PR-02, 03, 06, 09, 11, 12, 13, 14.

---

## DT-16 — PR-14 menée seule, en fin de séquence

**Décision.** PR-14 (anglais) n'est menée en parallèle d'aucune autre.

**Justification.** Elle restructure `T` (`ui.js`) et touche toutes les chaînes et tous les composants de texte. Menée avant que la structure soit stabilisée, elle serait à refaire ; menée en parallèle, elle entre en conflit avec toute PR en vol.

**Impact PR.** PR-14.

---

## DT-17 — Île JSON comme mécanisme unique de passage des chaînes au client

**Décision.** Le passage de chaînes et de données au script client se fait par **île JSON** (`<script type="application/json">`), comme le fait déjà `results.astro:69-92`. Le mécanisme `data-*` de `index.astro:25` est abandonné.

**Justification.** L'île JSON transporte des données structurées et échappe correctement ; `data-*` impose de sérialiser à la main et a conduit à la duplication D2 (pluralisation réécrite dans le script client faute d'accès à `ui.js`).

**Impact PR.** PR-09.

---

## DT-18 — `CHOICES` consommé depuis `score.js`, source unique

**Décision.** L'échelle `[-1, -0.5, 0, 0.5, 1]` n'existe qu'à un seul endroit : `score.js:39`.

**Justification.** Elle est aujourd'hui écrite **trois fois** (`score.js:39`, `index.astro:94`, `results.astro:101`), dont deux non testées. `choiceIndex()` est exportée et testée mais n'est utilisée nulle part.

**Impact PR.** PR-08 (restauration du brouillon), PR-10.

---

## DT-19 — `:has()` requis, sans repli

**Décision.** Le sélecteur `:has()` est une exigence de base assumée.

**Justification.** Il porte déjà l'état sélectionné (`styles.css:128`) sans repli. Le formaliser évite qu'un contributeur ajoute une couche de compatibilité non demandée.

**Impact PR.** PR-03, PR-06.

---

## DT-20 — Protocoles de comparaison de sortie pour les PR qui se prétendent neutres

**Décision.** Les PR qui se prétendent neutres en sortie sont validées par un protocole de comparaison explicite, jamais par appréciation.

**Justification.** C'est le seul critère acceptable pour une refactorisation neutre. Sans lui, PR-05 introduirait des écarts qui ne seraient attribués à aucune PR ultérieure.

**Trois protocoles distincts, selon ce que la PR change :**

| PR | Ce qui change | Protocole |
|---|---|---|
| **PR-03** | Le style uniquement, **aucun balisage** | **HTML compilé identique octet à octet** sur les quatre pages. Seul le fichier CSS émis diffère. Toute différence dans un `.html` signifie que la PR a débordé |
| **PR-05** | L'emplacement du balisage, **rien d'autre** | **HTML compilé identique octet à octet, différence nulle**, sur les quatre pages |
| **PR-10** | Le **mode de production** du HTML (statique au lieu de client) | Les octets changent nécessairement. La comparaison porte sur le **texte rendu extrait du DOM final** — après exécution du script, questions masquées exclues — et sur l'**ordre** des enregistrements et des questions, sur trois jeux de réponses : aucune, partielles, 30 |

**Aucune différence n'est justifiable.** Une formulation antérieure admettait des différences « comprises et justifiées » ; elle est abandonnée parce qu'une échappatoire subjective sur le seul critère d'une PR rend ce critère inopposable. Si une différence apparaît, la PR est bloquée et la cause corrigée.

**Impact PR.** PR-03, PR-05, PR-10.
