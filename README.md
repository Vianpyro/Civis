# 🏛️ Civis

**Un questionnaire politique à l'aveugle.**

Civis présente des propositions tirées des programmes officiels **sans dire de
qui elles viennent**. Vous vous positionnez, et l'affiliation n'est révélée
qu'à la fin.

## Pourquoi

Beaucoup de gens votent pour une étiquette avant de voter pour des idées. Retirer
l'étiquette pendant qu'on se positionne, c'est retirer le biais d'appartenance.
Ce n'est pas un sondage d'opinion : l'objectif est que vous découvriez vos
propres réponses, pas que nous mesurions les vôtres.

Deux conséquences qui gouvernent tout le reste :

- **Aucun nom de parti, logo, couleur ou indice** n'atteint le navigateur avant
  la dernière réponse. C'est structurel, pas déclaratif : le fichier de
  questions ne contient aucune donnée de parti, donc la page du questionnaire ne
  peut pas en révéler.
- **Aucune statistique agrégée pendant le questionnaire.** Afficher « 78 % sont
  d'accord » avant que vous ayez répondu réintroduit exactement le biais de
  conformité que l'outil sert à supprimer.

## Vie privée

Aucun résultat individuel n'est stocké. Pas de compte, pas de session, pas de
cookie, pas d'analytics tiers.

Si vous acceptez de contribuer aux statistiques (activé par défaut, désactivable
d'une case), **chaque réponse part dans une requête indépendante**, sans
identifiant, sans horodatage et sans lien avec les autres. Le serveur n'a aucune
colonne permettant de rapprocher deux réponses. C'est ce qui maintient le projet
hors du champ de l'article 9 du RGPD : nous ne constituons jamais un profil
d'opinions politiques, même transitoirement. Refuser n'envoie rien du tout.

## Vérifiabilité

Chaque question porte l'URL du document officiel dont elle dérive et la citation
exacte, affichées sur la page de résultats. La CI échoue si une citation
n'apparaît pas **mot pour mot** dans le document qu'elle cite — la neutralité est
vérifiée par une machine, pas affirmée dans un README.

Les empreintes SHA-256 des documents sont commitées. Quand un parti republie son
programme, une ligne change dans un fichier, une pull request s'ouvre, et
l'historique git montre publiquement ce qui a bougé et quand.

## Architecture

```
content/    JSON versionné — git est la base de données des questions
pipeline/   Python : téléchargement, empreintes, extraction, génération LLM hors-ligne
web/        Astro statique, i18n fr/en, scoring intégralement côté client
api/        Rust + axum + SQLite : deux endpoints de compteurs anonymes
```

| Domaine | Rôle | Technologie |
|---|---|---|
| Contenu | Programmes, questions, empreintes, historique diffable | Git + JSON |
| Pipeline | Fetch, diff par empreinte, brouillons de questions | Python + API Claude (batch) |
| Interface | Questionnaire aveugle, scoring, révélation | Astro (statique) |
| Compteurs | Agrégats anonymes | Rust + SQLite |

Il n'y a pas de base de données pour les questions, les programmes ou les
empreintes : git remplit ce rôle mieux, et son historique est un argument de
transparence. SQLite ne contient que des entiers. Si la base disparaît, on perd
des statistiques, jamais le produit.

## Démarrer

```bash
# Contenu : télécharger les documents officiels et vérifier les citations
pip install -r pipeline/requirements.txt
python -m pipeline.run --election fr-2027
python -m pipeline.check

# Interface
cd web && npm install && npm run dev

# Compteurs
cd api && cargo run
```

Le front lit l'API à l'adresse `PUBLIC_CIVIS_API` (`web/.env.development` la
pointe sur `http://127.0.0.1:8787` en développement). **Sans elle, le site est
complet** : le questionnaire, le score et la révélation sont intégralement
côté client. Seule la section « réponses des autres participants » disparaît —
et avec elle la case d'opt-in, puisqu'il n'y aurait nulle part où envoyer quoi
que ce soit.

## Déploiement

Le site est statique : `.github/workflows/pages.yml` le publie sur GitHub Pages
à chaque push sur `main`, après avoir fait tourner la vérification de contenu et
les tests de scoring. Il suffit d'activer Pages avec la source **GitHub Actions**
(Settings → Pages → Build and deployment → Source).

Sans compteurs, c'est tout : `https://vianpyro.github.io/Civis/` fonctionne de
bout en bout, on perd les statistiques agrégées et rien d'autre.

Pour brancher les compteurs plus tard, déployer `api/` là où un processus peut
tourner avec un disque (Fly.io, un VPS, n'importe quoi qui garde un fichier
SQLite), puis définir la variable de dépôt `PUBLIC_CIVIS_API` sur son URL
(Settings → Secrets and variables → Actions → Variables). Le prochain build
fait réapparaître la case d'opt-in et la section des agrégats. L'API a besoin
de `CIVIS_QUESTIONS` (chemin vers `content/questions/fr-2027.json`), `CIVIS_DB`
et `CIVIS_ADDR`.

Sur un nom de domaine, mettre `BASE = ""` et `site` dans
[`web/astro.config.mjs`](web/astro.config.mjs) : tous les liens internes
dérivent de `BASE_URL`, il n'y a rien d'autre à changer.

### Vérifications

```bash
python -m pipeline.check          # cohérence du contenu, citations mot pour mot
cd web && npm test                # scoring
cd api && cargo test              # compteurs
```

### Génération des questions

```bash
export ANTHROPIC_API_KEY=...
python -m pipeline.run --step generate
```

Un lot est envoyé à l'API Claude hors-ligne et écrit un brouillon dans
`review/`. **Rien n'entre dans `content/questions/` sans relecture humaine**, et
aucun appel LLM n'a lieu à l'exécution du site.

## État

MVP présidentielle française 2027. Les programmes 2027 n'étant pas encore
publiés, le jeu de données démarre sur les derniers documents officiels
réellement parus (législatives 2024, pages de programme officielles) — voir
[content/README.md](content/README.md). Le schéma accueille d'autres pays sans
migration ; aucune couche d'abstraction ne sera écrite avant le deuxième pays.

## Accessibilité

Le questionnaire est un formulaire HTML natif : groupes de boutons radio dans
des `fieldset` légendés, navigation clavier complète, focus toujours visible,
progression annoncée en `aria-live`. Un outil civique inutilisable au lecteur
d'écran n'est pas un outil civique.

## Contribuer

Les corrections de contenu comptent autant que le code : une citation tronquée,
une question orientée, une position mal attribuée sont des bugs. Le schéma et
les invariants sont décrits dans [content/README.md](content/README.md).

## Licence

Voir [LICENSE](LICENSE).
