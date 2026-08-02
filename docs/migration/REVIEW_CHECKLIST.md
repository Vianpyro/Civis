# Civis — Checklist de revue

**Usage :** à passer avant chaque fusion, sur toute PR touchant `web/`.
**Règle :** **une seule réponse défavorable justifie le rejet**, quelle que soit la qualité du reste. Une violation de principe ou d'invariant arrête la discussion avant l'examen des mérites.

**Modification des règles.** Ces règles se modifient par une PR dédiée, sans changement d'interface, datée, qui expose le principe concerné et la raison. **Une règle contournée dans une PR de fonctionnalité est une règle violée**, quelle que soit la justification.

---

## A. Périmètre

| # | Question | Rejet si |
|---|---|---|
| A1 | La PR correspond-elle à un fichier `PR-XX.md` existant ? | Non |
| A2 | Tous les fichiers modifiés figurent-ils dans « Fichiers concernés » de ce document ? | Non |
| A3 | Un fichier de la liste « Fichiers interdits » est-il modifié ? | Oui |
| A4 | La PR traite-t-elle une question ouverte (OQ) sans décision explicite du responsable ? | Oui |
| A5 | La PR fusionne-t-elle deux PR de la feuille de route ? | Oui |
| A6 | La PR modifie-t-elle `api/`, `content/` ou `pipeline/` ? | Oui, sauf mention explicite dans le document de la PR |

---

## B. Preuve et affirmation

| # | Question | Principe | Rejet si |
|---|---|---|---|
| B1 | Une phrase affirme-t-elle une propriété du projet **sans indiquer le geste précis permettant de la contredire** ? | P1 | Oui |
| B2 | Une revendication est-elle formulée plus largement que ce qui est démontrable ? | P2 | Oui |
| B3 | Une propriété vraie du dépôt devient-elle plus difficile à atteindre depuis l'interface ? | P10 | Oui |
| B4 | L'appareil de version est-il absent d'une page ajoutée ? | P6 | Oui |
| B5 | Un identifiant de build, une date ou une empreinte est-il affiché avec une valeur factice ? | P1, DT-13 | Oui |

---

## C. Provenance et registres

| # | Question | Référence | Rejet si |
|---|---|---|---|
| C1 | Un texte que nous avons écrit peut-il être confondu avec un texte que nous citons ? | P3 | Oui |
| C2 | Le sérif est-il employé ailleurs que pour du texte cité ? | Système §3.1 | Oui |
| C3 | Une citation est-elle tronquée, ou séparée de son document, de sa date et de son empreinte ? | INV-06 | Oui |
| C4 | Une traduction remplace-t-elle un texte d'origine au lieu de l'accompagner ? | DP-18 | Oui |
| C5 | Un passage dans une langue autre que celle du document est-il ajouté **sans attribut de langue** ? | WCAG 3.1.2 | Oui |
| C6 | *(Jugement humain, non testable)* Le marquage de registre est-il déclaré une fois par contexte uniforme, et par bloc en contexte mixte ? | Système §3.7 | Marquage absent ou systématiquement répété |

---

## D. Nombres et limites

| # | Question | Référence | Rejet si |
|---|---|---|---|
| D1 | Un nombre est-il affiché sans son dénominateur, ou avec un dénominateur d'un poids visuel moindre ? | P4, INV-13 | Oui |
| D2 | Un pourcentage est-il calculé sur un effectif inférieur au seuil publié ? | DP-15 | Oui |
| D3 | Une échelle graphique commune est-elle appliquée à des bases différentes ? | DP-10 | Oui |
| D4 | Un composant de portée devient-il fermable, repliable ou moins visible ? | DP-13 | Oui |
| D5 | Le niveau de confiance ou la couverture est-il retiré d'un résultat ? | DP-11, DP-12 | Oui |
| D6 | Un libellé d'effectif évoque-t-il un nombre de **personnes** ou de **participants** ? | DT-11 | Oui |
| D7 | Un seuil (confiance, pourcentage) existe-t-il à plus d'un endroit du code, ou une valeur de seuil est-elle **recopiée** dans la page de méthodologie au lieu d'être lue depuis `score.js` ? | DP-11, DP-15 | Oui |
| **D8** | Une borne de confiance ou le seuil de pourcentage est-il **modifié** par cette PR ? (bornes définitives : 0 / 1–4 / 5–9 / ≥ 10 pour la confiance ; 100 réponses pour le pourcentage) | DP-11, DP-15 | Oui, sauf PR dédiée modifiant explicitement la décision |
| **D9** | Le **bloc de provenance** en tête des résultats est-il retiré, replié, déplacé après les résultats, ou privé des empreintes ? | **DP-28**, P1, P4 | Oui |

---

## E. Neutralité

| # | Question | Référence | Rejet si |
|---|---|---|---|
| E1 | La PR introduit-elle **une valeur chromatique**, quelle qu'elle soit ? | DP-22, INV-12 | Oui |
| E2 | Une information est-elle portée par la seule couleur ou la seule valeur de gris ? | WCAG 1.4.1 | Oui |
| E3 | Une métadonnée propre à un item apparaît-elle **pendant** la passation ? | INV-01 | Oui |
| E4 | Un élément change-t-il d'apparence en fonction des réponses déjà données, avant la fin ? | INV-01, INV-02 | Oui |
| E5 | Une information sur les autres participants devient-elle accessible avant la révélation ? | INV-02, P7 | Oui |
| E6 | Un import de `content/programs/` ou de `*.positions.json` est-il ajouté à un composant utilisé par le questionnaire, **y compris de façon transitive** ? | INV-01 | Oui |
| E7 | Un pictogramme ou une icône thématique est-il ajouté à une question ? | INV-01 | Oui |

---

## F. Influence

| # | Question | Référence | Rejet si |
|---|---|---|---|
| F1 | **Test décisif** — cet élément informerait-il moins s'il était retiré, ou rendrait-il seulement l'abandon moins probable ? | P9 | Second cas |
| F2 | La PR introduit-elle un badge, un témoignage, un compteur d'utilisateurs, un classement, une comparaison sociale, une étiquette de profil, un partage de résultat ou une mécanique de progression ? | Anti-principes | Oui |
| F3 | Une réponse est-elle présélectionnée, ou l'interface avance-t-elle automatiquement après une sélection ? | DP-25 | Oui |
| F4 | La PR fait-elle varier l'instrument entre deux utilisateurs autrement que par le tirage d'ordre documenté ? | INV-18 | Oui |
| F5 | L'interface emprunte-t-elle des signes d'officialité institutionnelle ? | Anti-principes | Oui |
| F6 | Une barre de progression graphique est-elle introduite ? | DP-20 | Oui |
| **F7** | Les **libellés affichés de l'échelle** varient-ils selon la largeur du viewport, ou diffèrent-ils du jeu unique arrêté par DP-26 ? | **INV-18, DP-26** | Oui |
| **F8** | L'**en-tête du questionnaire** dépasse-t-il cinq énoncés, ou un énoncé dépasse-t-il 120 caractères, ou un bouton d'action autre que le lien vers la méthodologie y est-il ajouté ? | **DP-27, DP-07** | Oui |

---

## G. Forme

| # | Question | Référence | Rejet si |
|---|---|---|---|
| G1 | Une valeur d'espacement hors des cinq autorisées (4, 8, 16, 32, 64 px) est-elle introduite ? | Système §3.5 | Oui |
| G2 | Une taille de police hors des six autorisées est-elle introduite ? | Système §3.2 | Oui |
| G3 | Une graisse change-t-elle en fonction d'un état, provoquant un décalage de mise en page ? | Système §3.3 | Oui |
| G4 | Une animation absente de la liste autorisée est-elle ajoutée, ou une animation autorisée dépasse-t-elle 120 ms ? | DP-21 | Oui |
| G5 | Un élément décoratif sans fonction informationnelle est-il ajouté ? | Système §1.3 | Oui |
| G6 | Un attribut `style=` inline est-il présent dans un composant ou une page ? | DT-04 | Oui |
| G7 | Le terme « carte » est-il employé à la place d'« enregistrement » ? | Système §5.2 | Oui |
| G8 | La liste d'exceptions du test de jetons est-elle allongée ? | DT-04 | Oui, sauf PR dédiée au système |

---

## H. Accessibilité

| # | Question | Référence | Rejet si |
|---|---|---|---|
| H1 | Le contraste du texte descend-il sous 7:1, ou celui d'une bordure d'affordance sous 3:1 ? | INV-12, WCAG 1.4.11 | Oui |
| H2 | Une cible de pointage descend-elle sous 44×44 px ? | Système §7.3 | Oui |
| H3 | Un contrôle natif est-il masqué, remplacé ou privé de sa sémantique ? | INV-10 | Oui |
| H4 | Le focus est-il supprimé, atténué, ou rendu inatteignable sous un élément flottant ? | INV-11 | Oui |
| H5 | L'ordre de tabulation diffère-t-il de l'ordre visuel ? | INV-17, DT-08 | Oui |
| H6 | L'échelle de réponse se replie-t-elle à une largeur quelconque entre 320 px et 1600 px ? | Système §5.3 | Oui |
| H7 | Un libellé affiché abrégé prive-t-il le contrôle de son **nom accessible complet** ? | — | Oui |
| H8 | Une région vivante annonce-t-elle un changement déjà perceptible autrement ? | Système §7.8 | Oui |
| H9 | Une défaillance de service se traduit-elle par la **disparition silencieuse** d'une section ? | INV-14, P8 | Oui |
| H10 | Le contenu est-il perdu ou tronqué à 320 px ou à 200 % de zoom ? | WCAG 1.4.4, 1.4.10 | Oui |

---

## I. Rédaction

| # | Question | Référence | Rejet si |
|---|---|---|---|
| I1 | Le texte contient-il une formule de réassurance (« nous respectons votre vie privée », « en toute transparence ») ? | Système §8.2 | Oui |
| I2 | Le texte s'auto-qualifie-t-il (fiable, neutre, objectif, impartial, rigoureux) ? | Système §8.2 | Oui |
| I3 | Le texte contient-il un superlatif, une injonction à poursuivre, ou un point d'exclamation ? | Système §8.2 | Oui |
| I4 | Le texte contient-il du jargon juridique dans le consentement ? | DP-16 | Oui |
| I5 | Une date relative (« récemment », « à jour ») est-elle employée à la place d'une date absolue ? | Système §8.3 | Oui |
| I6 | Un terme du lexique fixé est-il remplacé par un synonyme (« parti » pour « formation », « carte » pour « enregistrement ») ? | Glossaire | Oui |
| I7 | Le « nous » est-il employé pour une intention plutôt que pour un acte accompli ? | Système §8.1 | Oui |
| I8 | Le « vous » est-il employé pour prescrire, qualifier ou encourager l'utilisateur ? | Système §8.1 | Oui |
| I9 | Un terme technique est-il remplacé par un terme vague et rassurant (« sécurisé » au lieu de « SHA-256 ») ? | Système §8.4 | Oui |
| **I10** | Un **nom de fichier, un identifiant, un commentaire ou un message de commit** introduit par cette PR est-il rédigé en français ? (le contenu affiché reste en français ; le code reste en anglais) | **INV-15** | Oui |

---

## J. Sécurité et données

| # | Question | Référence | Rejet si |
|---|---|---|---|
| J1 | Une occurrence de `innerHTML` ou d'échappement manuel subsiste-t-elle après PR-10 ? | §17 | Oui |
| J2 | `localStorage` est-il utilisé ? | DP-09 | Oui |
| J3 | Les réponses sont-elles groupées en un envoi unique, ou un identifiant de corrélation est-il ajouté ? | INV-04 | Oui |
| J4 | Un envoi a-t-il lieu alors que la contribution est refusée ? | INV-05 | Oui |
| J5 | Une requête vers un domaine tiers est-elle introduite (police, script, mesure d'audience) ? | INV-16 | Oui |
| J6 | Une colonne, un horodatage ou un identifiant est-il ajouté côté API ? | INV-03 | Oui |
| **J7** | Un contenu **autre que la section des statistiques** dépend-il d'une réponse de l'API ? Ou `API` vide est-il traité comme une erreur plutôt que comme un déploiement supporté ? | **INV-08** | Oui |
| **J8** | Un appel réseau — vers l'API du projet ou ailleurs — est-il introduit dans le **chemin de calcul du résultat** ? Une réponse complète est-elle transmise à un service pour être évaluée ? | **INV-09** | Oui |

---

## K. Tests et dette

| # | Question | Rejet si |
|---|---|---|
| K1 | Les tests automatiques listés dans le document de la PR sont-ils tous verts ? | Non |
| K2 | Le contrôle d'aveuglement (PR-01) passe-t-il ? | Non |
| K3 | Les vérifications manuelles M1–M8 listées dans le document de la PR ont-elles été effectuées et consignées ? | Non |
| K4 | Une nouvelle dépendance npm est-elle ajoutée ? | Oui |
| K5 | Une duplication est-elle introduite ou une duplication existante (D1–D6) est-elle aggravée ? | Oui |
| K6 | Un composant est-il créé sans correspondre à un besoin identifié dans la feuille de route ? | Oui |
| K7 | Un commentaire de code documente-t-il une règle abolie par le système d'interface ? | Oui |
| K8 | La logique non triviale ajoutée est-elle dépourvue de tout contrôle exécutable ? | Oui |
| **K9** | La PR introduit-elle dans `web/` une **copie** d'une donnée qui vit dans `content/` — question, libellé, citation, empreinte, date, chiffre de couverture, seuil ? (elle doit être **lue**, jamais recopiée) | Oui — **INV-07** |
| **K10** | Une exception du test de jetons est-elle retirée **en totalité** alors qu'elle couvre des fichiers hors du périmètre de la PR ? (les exceptions `inline-styles-questionnaire` et `inline-styles-resultats` sont retirées séparément, par PR-04 et PR-10) | Oui |

---

## L. Réversibilité

| # | Question | Rejet si |
|---|---|---|
| L1 | La PR modifie-t-elle un format de données persistant sans mention dans son document ? | Oui |
| L2 | La PR laisse-t-elle le produit dans un état intermédiaire incohérent si elle est déployée seule ? | Oui |
| L3 | La PR crée-t-elle une dépendance non déclarée envers une PR non encore fusionnée ? | Oui |

---

## Couverture des invariants

Chaque invariant doit être opposable par au moins un point de cette checklist. Table de
correspondance, à maintenir à jour lorsqu'un invariant est ajouté :

| Invariant | Points | Invariant | Points |
|---|---|---|---|
| INV-01 Aveuglement | E3, E4, E6, E7 | INV-10 Contrôles natifs | H3 |
| INV-02 Pas de stats avant révélation | E5 | INV-11 Focus | H4 |
| INV-03 Aucun résultat individuel stocké | J6 | INV-12 Aucune teinte | E1, E2, H1 |
| INV-04 Incréments indépendants | J3 | INV-13 Nombre sans dénominateur | D1 |
| INV-05 Refuser n'envoie rien | J4 | INV-14 Absence affichée | H9 |
| INV-06 Citation exacte | C3 | INV-15 Langues | **I10** |
| | | INV-18 (libellés) | **F7** |
| INV-07 Git source de vérité | **K9** | INV-16 Dépendances tierces | J5 |
| INV-08 Complet sans l'API | **J7** | INV-17 Ordre de focus | H5 |
| INV-09 Scoring côté client | **J8** | INV-18 Instrument identique | F4 |

**18 invariants, 18 couverts.** Un invariant sans point de checklist est un invariant déclaré
protégé sans l'être : c'est un défaut de la checklist, pas de l'invariant.

---

## Récapitulatif de fusion

Avant de fusionner, la description de la PR doit contenir :

- [ ] Le numéro de PR et le lien vers `docs/migration/PR-XX.md`
- [ ] La liste des vérifications manuelles effectuées, avec leur résultat
- [ ] Pour **PR-03** : les ratios de contraste **mesurés**, pas affirmés, **et** le constat de HTML compilé identique octet à octet sur les quatre pages
- [ ] Pour **PR-05** : le constat de **différence nulle** de la sortie compilée sur les quatre pages
- [ ] Pour **PR-06** : le relevé du protocole des neuf largeurs (320, 360, 375, 414, 480, 600, 768, 1024, 1600 px)
- [ ] Pour **PR-07** : le relevé des cinq rechargements (ordre de tabulation) et la preuve d'absence de peinture dans l'ordre du fichier
- [ ] Pour **PR-10** : le constat de texte rendu et d'ordre identiques sur les trois jeux de réponses
- [ ] Pour **PR-11** : le relevé du cas `lr` avec le niveau de confiance recalculé à la main
- [ ] Pour **PR-12** : le relevé des trois messages d'absence
- [ ] La mention explicite de toute question ouverte rencontrée et **non tranchée**
