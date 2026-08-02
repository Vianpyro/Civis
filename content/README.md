# Schéma de contenu

```
sources/fr-2027/sources.json     documents officiels déclarés (id, parti, titre, url)
sources/fr-2027/<id>.sha256      « <empreinte>  <url> » — généré, commité
programs/fr-2027/<parti>.json    identité du parti + points de programme (citation)
questions/fr-2027.json           questions aveugles : id, thème, texte fr/en
questions/fr-2027.positions.json question → [{ point, stance }]
impacts/fr-2027.json             point → analyse de conséquences (relue)
```

## Pourquoi ce découpage

**Trois fichiers parce qu'il y a trois responsabilités**, et parce que la
séparation porte l'invariant produit.

`questions/<élection>.json` ne contient **aucune donnée de parti** : ni nom, ni
identifiant, ni position. Ce n'est pas une convention, c'est structurel — le
questionnaire ne peut pas révéler une affiliation qu'il n'a pas chargée. Si la
correspondance vivait dans le même fichier, l'invariant dépendrait de la
discipline du code client, donc d'une revue humaine à chaque changement.

`positions.json` est la table de correspondance. Elle est séparée parce que le
client ne la charge qu'après la dernière réponse ; elle est un fichier plutôt
qu'un champ parce que c'est exactement la frontière de chargement.

`programs/<parti>.json` porte la citation, une seule fois. Une question peut
s'appuyer sur plusieurs points, un point peut servir plusieurs questions, et une
citation dupliquée finirait par diverger de sa source.

## Les analyses de conséquences

`impacts/<élection>.json` décrit ce qu'une mesure prévoit, qui elle concerne et
quels effets sont attendus. **Un fichier satellite, pas un champ de
`programs/`** : `programs/` porte un invariant d'une phrase — toute chaîne
éditoriale qu'il contient figure mot pour mot dans le document source — et y
mêler de la prose déduite le détruirait. Les cadences diffèrent aussi : une
citation est stable des années, une analyse est régénérée à chaque changement de
modèle ou de consigne.

Chaque énoncé porte un `basis`. `text` signifie *soutenu par le document* et
**exige un `span`**, fragment copié à l'identique et vérifié en CI ; `inferred`
signifie *déduit*, et n'a pas de fragment à montrer. La distinction n'est pas
une étiquette : c'est la présence ou l'absence de la preuve. Le lecteur constate,
il ne nous croit pas.

`of` est l'empreinte **de la citation**, jamais du document : un PDF réexporté
change d'empreinte sans que son texte bouge, et indexer sur le document
périmerait tout à chaque republication cosmétique.

Le fichier a une **forme canonique** — clés de points triées, énoncés dans
l'ordre `implication`, `affected`, `effect`, indentation de deux espaces, saut de
ligne final. La CI resérialise et compare octet à octet : une régénération
machine et une correction à la main produisent le même fichier, donc des diffs
lisibles pour la relecture, qui est le filtre qui compte.

## Les empreintes plutôt qu'une base

`<id>.sha256` tient sur une ligne : `<empreinte>  <url>`. Quand un parti
republie son document, exactement une ligne change dans exactement un fichier.
Ce diff *est* l'argument de transparence — un lecteur voit qu'un programme a
bougé, quand, et sur quelle URL, sans nous faire confiance.

Les documents eux-mêmes ne sont pas commités : binaires, lourds, republiés
souvent. Ils vivent dans `.cache/`, que la CI reconstruit avant chaque
vérification.

## Ce que la CI garantit

`python -m pipeline.check` échoue si :

- une citation n'apparaît pas **mot pour mot** dans le document qu'elle cite ;
- une empreinte ne correspond pas à l'URL déclarée ;
- un identifiant de parti, un nom ou un sigle apparaît dans le fichier aveugle ;
- une question n'a aucune position, ou une position pointe un point inexistant ;
- deux positions du même parti répondent à la même question ;
- une analyse porte une clé inconnue, un point inexistant, une empreinte `of`
  qui n'est pas celle de la citation, un `span` introuvable dans le document,
  un groupe hors vocabulaire, un nombre d'énoncés hors des bornes, une date de
  relecture absente, ou une mise en forme non canonique ;
- un énoncé d'analyse contient un nom de formation, un terme évaluatif, un verbe
  de valeur, un intensificateur, un superlatif, un point d'exclamation, un
  quantificateur que son `span` ne porte pas, un chiffre absent du document, ou
  présente une déduction comme un fait.

La première est la seule qui compte vraiment : c'est elle qui rend la neutralité
vérifiable par une machine plutôt qu'affirmée dans un README.

Le lexique de neutralité (`pipeline/neutrality.py`) ne s'applique **qu'aux
énoncés que nous écrivons**, jamais à un `span` ni à une citation : un mot
d'appréciation dans un document officiel est le document qui parle, et le
bloquer reviendrait à censurer la source. Le lexique est court, en clair, et
s'étend par relecture — jamais par une exception pour une entrée. Il produit des
faux positifs : on reformule, la vérification stricte vaut mieux que la
vérification intelligente.

**Limite connue sur les quantificateurs anglais.** Un quantificateur n'est admis
que si le `span` le porte, et les `span` sont français. « Toutes les
collectivités… » passe donc si le document écrit « toutes », alors que « All
authorities… » échoue dans le même énoncé. La version anglaise se reformule sans
quantificateur. Le comportement est volontairement inchangé — voir R-9 dans
`docs/impacts/DECISION.md`.

**Elle échoue sur ce qui est faux, elle avertit sur ce qui manque.** Un point
sans analyse, ou une question dont seules certaines positions en ont une, sont
des états normaux d'un corpus en cours : la CI les signale et passe. Une question
partiellement couverte n'affiche simplement rien — comparer quatre positions dont
une seule est documentée avantagerait celle-là.

Conséquence à connaître : le sigle d'un parti qui est aussi un mot courant
(« Ensemble ») fait échouer la vérification s'il apparaît dans une question.
Reformuler la question — la vérification stricte vaut mieux que la vérification
intelligente.

## Ajouter un scrutin

Créer `sources/<élection>/sources.json`, puis `python -m pipeline.run --election
<élection>`. Rien dans le schéma n'est propre à la France : `stance` vaut −1 ou
+1, les thèmes sont un vocabulaire partagé, les identifiants de partis sont
locaux au dossier du scrutin. Aucune couche d'abstraction n'est prévue avant le
deuxième pays — il n'y en a pas besoin.

## Sources actuelles

Les programmes présidentiels 2027 n'existent pas encore. Le jeu de données
démarre donc sur les derniers documents officiels réellement publiés par chaque
formation (législatives 2024, pages de programme officielles), déclarés tels
quels dans `sources.json`. Quand les programmes 2027 paraîtront, ils remplaceront
ces entrées et le diff des empreintes montrera le remplacement.
