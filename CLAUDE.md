# Civis

Questionnaire politique « à l'aveugle » : des propositions issues des programmes
officiels, sans attribution, jusqu'à la révélation finale. Objectif : supprimer
le biais d'appartenance, pas mesurer une opinion.

## Invariants

- Aucune affiliation (nom, logo, couleur, indice) n'atteint le client avant que
  l'utilisateur ait répondu à tout.
- Les statistiques agrégées ne s'affichent qu'après le questionnaire — les
  montrer pendant réintroduit le biais de conformité.
- Aucun résultat individuel stocké. Aucune PII, session, IP ou horodatage fin.
- Chaque réponse remonte en incrément **indépendant**. Rien ne relie entre elles
  les réponses d'une même personne : c'est ce qui garde le projet hors du RGPD
  Art. 9 (profil d'opinions politiques). Ne pas grouper pour ajouter des
  corrélations.
- Agrégation par défaut, opt-out. Qui refuse n'envoie rien.
- Chaque question porte son URL de document officiel et la citation exacte.

## Où vivent les données

- **Git** = source de vérité : programmes, questions, empreintes de documents.
  L'historique diffable est un argument de transparence, pas un détail.
- **SQLite** = compteurs anonymes uniquement. Si la base brûle, on perd des
  stats, jamais le produit.

## Structure

```
content/    JSON versionné : sources/ (sha256), programs/, questions/
pipeline/   Python — fetch, diff par empreinte, génération LLM en batch hors-ligne
web/        Astro statique, i18n fr/en, scoring côté client
api/        Rust + axum + SQLite, deux endpoints de compteurs
```

## Commandes

<!-- ponytail: à remplir quand chaque brique existe -->

```
pipeline    python -m pipeline.run --election fr-2027
web         cd web && npm run dev
api         cd api && cargo run
checks      python -m pipeline.check && cd web && npm test && cd ../api && cargo test
```

## Langues

Contenu politique en français. Code, identifiants, commentaires en anglais.

## Travail

Dépôt petit : fais le travail directement. Pas de sous-agent pour de la
relecture ou de la vérification — elles restent dans la boucle principale.
Calibre la longueur des fichiers écrits sur ce que la tâche exige.

## Non-objectifs

PostgreSQL. Docker (MVP). Comptes, auth, sessions. Analytics tiers, cookies,
bannière de consentement. Abstraction multi-pays avant le second pays. Design
system. Back-office. API publique.
