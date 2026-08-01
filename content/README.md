# Schéma de contenu

```
sources/fr-2027/sources.json     documents officiels déclarés (id, parti, titre, url)
sources/fr-2027/<id>.sha256      « <empreinte>  <url> » — généré, commité
programs/fr-2027/<parti>.json    identité du parti + points de programme (citation)
questions/fr-2027.json           questions aveugles : id, thème, texte fr/en
questions/fr-2027.positions.json question → [{ point, stance }]
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
- deux positions du même parti répondent à la même question.

La première est la seule qui compte vraiment : c'est elle qui rend la neutralité
vérifiable par une machine plutôt qu'affirmée dans un README.

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
