# Civis — Invariants

**Objet :** ce document ne contient que des invariants. Un invariant est une propriété qui ne peut être cassée par aucune PR, sous aucune justification, sans une décision explicite du responsable du projet documentée dans `DECISIONS.md`.

**Format.** Pour chaque invariant : pourquoi il existe, ce qui le protège aujourd'hui, comment il peut être cassé, comment vérifier qu'il tient.

**Distinction importante.** Un invariant **protégé par une garantie structurelle** (la donnée n'existe pas là où elle pourrait fuir) est plus solide qu'un invariant **protégé par une règle de codage**. Le projet privilégie systématiquement le premier. Quand un invariant n'est protégé que par la discipline, c'est indiqué.

---

## Sommaire

| Id | Invariant | Nature de la protection |
|---|---|---|
| [INV-01](#inv-01--aveuglement-structurel) | Aveuglement structurel | Structurelle + test (PR-01) |
| [INV-02](#inv-02--aucune-statistique-avant-la-révélation) | Aucune statistique avant la révélation | Structurelle |
| [INV-03](#inv-03--aucun-résultat-individuel-stocké) | Aucun résultat individuel stocké | Structurelle (schéma) |
| [INV-04](#inv-04--incréments-indépendants-et-non-corrélables) | Incréments indépendants et non corrélables | Structurelle + discipline |
| [INV-05](#inv-05--refuser-nenvoie-rien) | Refuser n'envoie rien | Discipline |
| [INV-06](#inv-06--citation-exacte-et-document-officiel) | Citation exacte et document officiel | Test CI (`pipeline.check`) |
| [INV-07](#inv-07--git-source-de-vérité-sqlite-compteurs-seulement) | Git source de vérité, SQLite compteurs | Structurelle (schéma) + checklist **K9** |
| [INV-08](#inv-08--le-site-est-complet-sans-lapi) | Le site est complet sans l'API | Checklist **J7** + M8 |
| [INV-09](#inv-09--scoring-intégralement-côté-client) | Scoring intégralement côté client | Structurelle + checklist **J8** |
| [INV-10](#inv-10--contrôles-natifs-jamais-masqués) | Contrôles natifs jamais masqués | Checklist **H3** + M5 |
| [INV-11](#inv-11--focus-jamais-supprimé) | Focus jamais supprimé | Checklist **H4** + M1 |
| [INV-12](#inv-12--aucune-teinte-aucune-information-par-la-couleur) | Aucune teinte | Test (PR-03) + checklist **E1, E2, H1** |
| [INV-13](#inv-13--aucun-nombre-sans-son-dénominateur) | Aucun nombre sans dénominateur | Checklist **D1** (revue humaine) |
| [INV-14](#inv-14--une-absence-saffiche-comme-absence) | Une absence s'affiche comme absence | Checklist **H9** + M8 |
| [INV-15](#inv-15--langues-contenu-français-code-anglais) | Contenu français, code anglais | Checklist **I10** |
| [INV-16](#inv-16--aucune-dépendance-tierce-à-lexécution) | Aucune dépendance tierce à l'exécution | Discipline |
| [INV-17](#inv-17--lordre-de-focus-est-lordre-visuel) | L'ordre de focus est l'ordre visuel | Discipline + M1 |
| [INV-18](#inv-18--instrument-identique-pour-tous) | Instrument identique pour tous | Checklist **F4** et **F7** |

---

## INV-01 — Aveuglement structurel

**Énoncé.** Aucune affiliation politique — identifiant, nom, sigle, logo, couleur, indice — n'atteint le navigateur avant que l'utilisateur ait répondu à tout.

**Pourquoi il existe.** C'est la raison d'être du produit. Sans lui, Civis est un quiz politique de plus. L'objectif est de supprimer le biais d'appartenance, ce qui suppose que l'étiquette soit absente **pendant** que l'utilisateur se positionne.

**Ce qui le protège.**
- **Garantie structurelle :** `web/src/pages/[lang]/index.astro` n'importe que `content/questions/fr-2027.json`, fichier qui ne contient aucune donnée de formation. La page ne peut pas révéler ce qu'elle ne contient pas.
- **À partir de PR-01 :** un contrôle exécuté après `npm run build` parcourt la page de questionnaire compilée et tous les avoirs JavaScript qu'elle référence, et échoue si l'un d'eux contient un identifiant, un nom ou un sigle lu depuis `content/programs/`.

**Comment il peut être cassé.**
1. Ajouter un import de `content/programs/` ou de `content/questions/*.positions.json` dans le questionnaire ou dans un composant qu'il utilise — **y compris un import transitif** via un composant partagé avec la page de résultats.
2. Introduire une couleur, un pictogramme ou un ordre associable à une formation (motif de DP-22 et de l'interdiction des icônes thématiques).
3. Afficher une métadonnée par question pendant la passation — par exemple le nombre de formations positionnées, qui révélerait la structure du corpus.
4. Faire figurer un nom de formation dans un énoncé de question (défaut de contenu, voir OQ-08).

**Comment vérifier.** Le contrôle de PR-01 doit passer. En revue : tout import ajouté à un composant utilisé par le questionnaire doit être justifié. **Attention aux composants partagés entre les deux pages** — c'est le vecteur le plus probable après PR-05.

---

## INV-02 — Aucune statistique avant la révélation

**Énoncé.** Aucun agrégat, aucune donnée sur les autres participants n'est affichée avant que les réponses de l'utilisateur soient figées.

**Pourquoi il existe.** Afficher « 78 % sont d'accord » avant que l'utilisateur ait répondu réintroduit exactement le biais de conformité que l'outil sert à supprimer.

**Ce qui le protège.** Le questionnaire n'émet aucune requête réseau hormis l'envoi des réponses à la soumission. Le `GET /counts` n'est appelé que depuis `results.astro:165`.

**Comment il peut être cassé.** Précharger les compteurs depuis le questionnaire « pour accélérer l'affichage ultérieur » ; afficher un aperçu après chaque réponse ; afficher un effectif dans la barre d'action.

**Comment vérifier.** Onglet réseau ouvert pendant une passation complète : aucune requête sortante avant la soumission.

---

## INV-03 — Aucun résultat individuel stocké

**Énoncé.** Aucun résultat individuel n'est stocké côté serveur. Aucune PII, aucune session, aucune adresse IP conservée, aucun horodatage fin.

**Pourquoi il existe.** Constituer un enregistrement d'opinions politiques rattachable à une personne ferait entrer le projet dans le champ de l'article 9 du RGPD.

**Ce qui le protège.** Le schéma lui-même : `counts(question TEXT, choice INTEGER, n INTEGER, PRIMARY KEY(question, choice))`. Il n'existe **aucune colonne** susceptible de porter une identité ou un instant.

**Comment il peut être cassé.** Ajouter une colonne (`created_at`, `session`, `client`) « pour le débogage » ; activer une journalisation des requêtes côté serveur ou côté hébergeur ; ajouter un identifiant de corrélation dans le corps de la requête.

**Comment vérifier.** Le schéma de `api/src/main.rs:37-45` reste à trois colonnes. Aucune PR du chantier ne touche `api/` (DT-10) : toute modification y est hors périmètre et doit être justifiée séparément.

**Limite connue et à énoncer.** Le serveur voit l'adresse IP de la requête, comme tout serveur. Elle n'est pas conservée, mais nous ne contrôlons pas ce que fait l'hébergeur. P2 impose que ce résidu soit **écrit dans l'interface**, pas seulement dans un commentaire de code (`index.astro:99-103`).

---

## INV-04 — Incréments indépendants et non corrélables

**Énoncé.** Chaque réponse remonte dans une requête indépendante, en ordre aléatoire, sans identifiant, sans horodatage et sans lien avec les autres.

**Pourquoi il existe.** C'est ce qui empêche la reconstitution d'un profil d'opinions, **même transitoirement**, y compris dans la requête réseau elle-même.

**Ce qui le protège.** `index.astro:104-111` : une boucle sur les réponses mélangées, une requête `POST /counts` par réponse, corps limité à `{question, choice}`, `keepalive: true`, échec silencieux.

**Comment il peut être cassé.** Grouper les réponses en un envoi unique « pour réduire le nombre de requêtes » — c'est l'optimisation la plus naturelle et elle reconstitue le profil dans le corps de la requête. Ajouter un identifiant de lot. Conserver l'ordre du questionnaire dans la séquence d'envoi.

**Comment vérifier.** Onglet réseau à la soumission : autant de requêtes que de réponses, ordre non corrélé à l'ordre d'affichage, corps limité à deux champs.

---

## INV-05 — Refuser n'envoie rien

**Énoncé.** Quand l'utilisateur décoche la contribution, **rien n'est envoyé du tout**.

**Pourquoi il existe.** C'est la contrepartie qui rend l'opt-out (DP-04) défendable. Un opt-out qui enverrait quand même une donnée « anonyme » viderait la décision de son sens.

**Ce qui le protège.** `index.astro:99` : la boucle d'envoi est entièrement conditionnée. Sans service configuré, aucun opt-in n'est offert et il n'y a rien à consentir.

**Comment il peut être cassé.** Envoyer un « ping » de complétion ; envoyer les réponses mais marquées comme exclues ; conserver un compteur de refus.

**Comment vérifier.** Onglet réseau à la soumission avec la case décochée : **zéro requête sortante**.

---

## INV-06 — Citation exacte et document officiel

**Énoncé.** Chaque position affichée porte la citation exacte du document officiel et son URL. La CI échoue si une citation n'apparaît pas **mot pour mot** dans le document cité.

**Pourquoi il existe.** C'est la preuve du produit. La neutralité est vérifiée par une machine, pas affirmée dans un README.

**Ce qui le protège.** `pipeline/check.py`, exécuté en CI avant le build. Hors ligne, la vérification est **signalée comme sautée, jamais silencieusement validée**.

**Comment il peut être cassé.** Tronquer une citation par la mise en page (ellipse CSS, hauteur maximale, repli) — une citation raccourcie est une citation altérée. Traduire une citation en substitution de l'original (interdit par DP-18). Séparer une citation de son document, de sa date et de son empreinte.

**Comment vérifier.** `python -m pipeline.check` passe. En revue : aucun style de troncature n'est appliqué au composant Citation.

---

## INV-07 — Git source de vérité, SQLite compteurs seulement

**Énoncé.** Programmes, questions, positions et empreintes vivent en JSON versionné. SQLite ne contient que des entiers.

**Pourquoi il existe.** L'historique diffable est un argument de transparence. Si la base disparaît, on perd des statistiques, jamais le produit.

**Ce qui le protège.** Le schéma de la table ; l'absence de toute écriture de contenu par l'API ; `astro.config.mjs:21` (`fs.allow: [".."]`) qui permet d'importer `content/` directement plutôt que d'en maintenir une copie dans `web/`.

**Comment il peut être cassé.** Recopier du contenu dans `web/` « pour simplifier les imports » : la copie divergera. Stocker une question, un libellé ou une empreinte en base. **Vecteur le plus probable : PR-13**, qui manipule sources, dates et empreintes et pourrait les recopier plutôt que les lire.

**Comment vérifier.** Point **K9** de la checklist de revue : *la PR introduit-elle dans `web/` une copie d'une donnée vivant dans `content/` — question, libellé, citation, empreinte, date, chiffre de couverture ?* `web/` ne contient aucune copie de `content/` ; la table reste à trois colonnes.

---

## INV-08 — Le site est complet sans l'API

**Énoncé.** Sans service de compteurs, le questionnaire, le calcul et la révélation fonctionnent intégralement. Seule la section d'agrégats disparaît, et avec elle la case de contribution.

**Pourquoi il existe.** Le produit ne doit dépendre d'aucun service pour remplir sa fonction. C'est aussi ce qui rend le déploiement GitHub Pages suffisant.

**Ce qui le protège.** `paths.js:18` : `API` vaut `""` quand la variable n'est pas définie, et ce cas est traité comme un **déploiement supporté, pas une erreur de configuration**. `index.astro:54` et `:63` conditionnent l'affichage de la case ; `results.astro:162` retire la section.

**Comment il peut être cassé.** Rendre un affichage dépendant d'une réponse de l'API ; considérer `API` vide comme une erreur ; afficher une case de contribution sans destination.

**Comment vérifier.** Point **J7** de la checklist : *un contenu autre que la section des statistiques dépend-il d'une réponse de l'API, ou `API` vide est-il traité comme une erreur plutôt que comme un déploiement supporté ?* Plus **M8** : build avec `PUBLIC_CIVIS_API` vide, puis build avec une valeur pointant vers un service injoignable. Dans les deux cas, questionnaire et résultats restent complets.

**Note.** PR-12 modifie la manière dont l'absence est **affichée** (P8), pas le fait qu'elle soit supportée.

---

## INV-09 — Scoring intégralement côté client

**Énoncé.** Aucune réponse n'est envoyée quelque part pour être évaluée. Le navigateur détient la seule copie d'un questionnaire complet.

**Pourquoi il existe.** Un service qui calculerait le résultat verrait le questionnaire complet d'une personne, ce qui reconstituerait le profil que INV-03 et INV-04 empêchent.

**Ce qui le protège.** `score.js` est un module pur, importé côté client. Aucun endpoint de calcul n'existe.

**Comment il peut être cassé.** Déporter le calcul « pour alléger le client » ; envoyer les réponses complètes pour produire une statistique croisée.

**Comment vérifier.** Point **J8** de la checklist : *un appel réseau, vers l'API du projet ou ailleurs, est-il introduit dans le chemin de calcul du résultat, ou une réponse complète est-elle transmise à un service ?* `score()` reste une fonction pure sans effet de bord.

---

## INV-10 — Contrôles natifs jamais masqués

**Énoncé.** Les `<input type="radio">` et `<input type="checkbox">` sont affichés, jamais masqués visuellement ni remplacés par une réimplémentation.

**Pourquoi il existe.** Le mode contraste forcé du système d'exploitation rend les contrôles selon ses propres couleurs, ce qui n'est possible que si les contrôles natifs sont réellement affichés. Par ailleurs, la sémantique native est correcte au lecteur d'écran sans une ligne d'ARIA.

**Ce qui le protège.** `index.astro:36` : le contrôle est dans le libellé, non masqué. Aucune règle de `styles.css` ne le dissimule.

**Comment il peut être cassé.** `appearance: none`, `opacity: 0`, `position: absolute` hors écran, ou tout remplacement par un élément stylé avec `role="radio"`. C'est la modification la plus tentante lors d'une refonte visuelle de l'échelle (PR-06).

**Comment vérifier.** **M5** : mode contraste forcé, les cinq options restent visibles et l'état sélectionné reste distinguable.

---

## INV-11 — Focus jamais supprimé

**Énoncé.** L'indicateur de focus n'est jamais supprimé, atténué, retardé ni animé.

**Pourquoi il existe.** Le formulaire est le produit. Un outil civique inutilisable au clavier n'est pas un outil civique.

**Ce qui le protège.** `styles.css:64-68`, avec un commentaire explicite. À partir de PR-03, l'anneau double achromatique garantit ≥ 3:1 contre **n'importe quelle** surface, y compris à l'intérieur d'un bloc sélectionné ou sur un bouton à fond `ink`.

**Comment il peut être cassé.** `outline: none` ; un anneau de teinte unique qui échoue sur un fond particulier ; un élément flottant qui recouvre l'élément focalisé (risque réel avec la barre d'action : la marge de défilement doit être suffisante).

**Comment vérifier.** **M1** sur les deux pages, en incluant les éléments situés en bas de page, sous la barre d'action.

---

## INV-12 — Aucune teinte, aucune information par la couleur

**Énoncé.** L'interface est achromatique. Aucune information n'est portée par la couleur, ni par une valeur de gris utilisée comme échelle.

**Pourquoi il existe.** Neutralité structurelle : en France, presque toute teinte est appropriée par une formation ou un courant. L'absence de teinte rend la faute impossible plutôt qu'improbable. Corollaire gratuit : WCAG 1.4.1 devient inviolable.

**Ce qui le protège.** À partir de PR-03 : le test de jetons échoue sur toute valeur colorimétrique littérale hors du fichier de jetons et sur toute propriété de teinte. Aucun jeton n'est nommé d'après une signification (`success`, `danger`, `primary`), donc aucun code couleur ne peut être dérivé du vocabulaire.

**Comment il peut être cassé.** Ajouter un accent « juste pour les liens » ; teinter un avertissement en jaune ou en rouge ; utiliser un dégradé de gris comme échelle de valeur dans une statistique (un remplissage plus sombre serait lu comme « plus » ou « pire ») ; teinter l'échelle de réponse du rouge au vert.

**Comment vérifier.** Le test de jetons passe. En revue : *cette PR introduit-elle une valeur chromatique ?* Une réponse positive est un rejet.

**Seuls écarts admis.** Les couleurs imposées par le système en mode contraste forcé ; les couleurs d'un document cité si un fac-similé était un jour affiché.

---

## INV-13 — Aucun nombre sans son dénominateur

**Énoncé.** Aucune mesure ne s'affiche sans sa base, dans la même phrase et au même poids visuel. Une mesure dont on ne peut pas afficher la base ne s'affiche pas.

**Pourquoi il existe.** Le corpus donne des dénominateurs de 4 à 19 selon la formation. Un nombre isolé y est un mensonge court.

**Ce qui le protège.** DP-10 place le dénominateur **dans la phrase** du résultat, ce qui le rend structurellement inséparable. DP-15 impose l'effectif sur les statistiques, et interdit tout pourcentage sous **100 réponses enregistrées pour la proposition** — seuil dérivé de la précision affichée, un point, comparée à la granularité réelle de la donnée, `100/n`.

**Comment il peut être cassé.** Reléguer la base en note, en gris, en petits caractères ; réintroduire un pourcentage ; appliquer une échelle graphique commune à des dénominateurs différents (affirmation d'équivalence).

**Comment vérifier.** Revue. Aucun test automatisé ne couvre cet invariant : il repose sur la lecture.

---

## INV-14 — Une absence s'affiche comme absence

**Énoncé.** Une donnée manquante, un service absent et une donnée nulle sont trois états distincts, textuellement distincts. Aucun ne se traduit par une disparition silencieuse.

**Pourquoi il existe.** Faire disparaître une section présente à l'utilisateur un état du monde différent du réel, sans qu'il puisse le savoir. Un instrument signale une mesure manquante ; il ne recompose pas son rapport autour du trou.

**Ce qui le protège.** Rien aujourd'hui : `results.astro:162-163` retire silencieusement la section. C'est un **écart connu**, corrigé par PR-12. Le pipeline applique déjà le principe (`check.py` signale les vérifications sautées).

**Comment il peut être cassé.** Un `catch` vide qui masque une section ; un rendu conditionnel qui confond « pas de service » et « pas de données ».

**Comment vérifier.** **M8** dans trois configurations : service non configuré, service injoignable, compteurs à zéro. Trois messages distincts.

---

## INV-15 — Langues : contenu français, code anglais

**Énoncé.** Le contenu politique et l'interface publique sont en français. Le code, les identifiants, les commentaires et les messages de commit sont en anglais.

**Pourquoi il existe.** Règle de projet déclarée dans `CLAUDE.md`. Elle évite le mélange de registres dans le code et garde le contenu dans la langue de ses sources.

**Ce qui le protège.** Le point **I10** de la checklist de revue. Le dépôt est cohérent aujourd'hui : commentaires et identifiants en anglais, chaînes d'interface en français dans `ui.js`.

**Comment il peut être cassé.** Nommer un composant, un fichier ou une variable en français ; rédiger un commentaire ou un message de commit en français. **Vecteur le plus probable : PR-05**, qui nomme huit à dix fichiers de composants d'un coup, et PR-14, qui restructure `T`.

**Comment vérifier.** Point **I10** : *un nom de fichier, un identifiant, un commentaire ou un message de commit introduit par cette PR est-il rédigé en français ?*

**Note.** DP-18 ne contredit pas cet invariant : l'anglais y est une **aide à la lecture** de l'interface publique, pas un changement de langue du contenu.

---

## INV-16 — Aucune dépendance tierce à l'exécution

**Énoncé.** Aucune police distante, aucun analytics, aucun CDN, aucun script externe, aucun cookie, aucune bannière de consentement.

**Pourquoi il existe.** Chaque requête vers un tiers contredit la revendication d'absence de traçage et introduit un point de défaillance. Une police distante ajoute en outre un décalage de rendu.

**Ce qui le protège.** `styles.css:32` : polices système. Aucune balise `<script>` externe, aucun `<link>` distant dans `Base.astro`. Une seule dépendance npm, de build (DT-01).

**Comment il peut être cassé.** Ajouter une police web « pour l'identité » (interdit : le sérif du système suffit et sert un rôle sémantique) ; ajouter un outil de mesure d'audience.

**Comment vérifier.** Onglet réseau : aucune requête vers un domaine tiers, sur aucune page.

---

## INV-17 — L'ordre de focus est l'ordre visuel

**Énoncé.** L'ordre de tabulation suit l'ordre du document, qui est l'ordre affiché.

**Pourquoi il existe.** Un utilisateur au clavier qui parcourt les questions dans un ordre différent de celui qu'il voit ne peut pas utiliser l'instrument.

**Ce qui le protège.** Aujourd'hui, la coïncidence : le DOM est l'ordre d'affichage. **PR-07 met cet invariant en danger** en introduisant un tirage d'ordre.

**Comment il peut être cassé.** Réordonner visuellement par une propriété de mise en page (`order` sur un conteneur flex ou grid) au lieu de déplacer les nœuds. C'est la solution qui vient naturellement, et elle casse **silencieusement** : rien à l'écran ne le révèle, seul un test au clavier le détecte. Interdite par DT-08. Autres vecteurs : `tabindex` positif, positionnement absolu déplaçant un élément hors de son rang.

**Comment vérifier.** **M1 impérativement sur PR-07** : tabuler après plusieurs rechargements et vérifier que le parcours suit l'ordre affiché à chaque fois.

---

## INV-18 — Instrument identique pour tous

**Énoncé.** Tous les utilisateurs répondent au même instrument. Aucun test A/B, aucune variation de formulation, aucune adaptation au comportement.

**Pourquoi il existe.** Deux raisons cumulées. **Méthodologique :** des participants qui ne répondent pas au même instrument produisent des agrégats non comparables, donc sans valeur. **Éthique :** faire varier la formulation d'un énoncé politique entre deux personnes revient à mener une expérimentation non consentie sur la formation d'opinions.

**Ce qui le protège.** Rien de mécanique. Le contenu est statique et identique pour tous, mais aucune barrière n'empêche d'introduire une variation.

**Comment il peut être cassé.** Introduire un test A/B sur une formulation ou sur l'ordre des options ; adapter l'interface au comportement de l'utilisateur ; modifier un énoncé sans changer sa version ; **faire varier les libellés de l'échelle selon la largeur du viewport**.

**Conséquence explicite sur les libellés de l'échelle (DP-26).** Un jeu de libellés qui changerait avec la largeur du viewport présenterait **des ancres différentes selon l'appareil** : un utilisateur sur téléphone et un utilisateur sur ordinateur ne répondraient pas au même instrument. C'est une variation de mesure entre sujets, et elle n'est pas couverte par l'exception ci-dessous. **Les libellés sont donc identiques à toutes les largeurs**, dimensionnés pour la plus contrainte (320 px).

**Comment vérifier.** Point **F7** de la checklist : *les libellés affichés de l'échelle varient-ils selon la largeur du viewport ?* Plus la revue pour le reste : toute modification d'un énoncé est un **changement de version de l'instrument**, daté et tracé dans l'historique.

**Exception unique et documentée.** Le tirage aléatoire de l'ordre (DP-14), qui est une propriété déclarée de l'instrument et doit être documentée en méthodologie.

**Limite connue.** `content/questions/fr-2027.json` n'a ni champ de version ni date par item : une reformulation ne laisse de trace que dans l'historique git. Voir OQ-04.
