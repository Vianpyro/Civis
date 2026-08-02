export const LANGS = ["fr", "en"];

// The full formulations. They are the accessible name of every scale control and
// the label used on the results page; they are no longer what the scale displays.
export const CHOICE_LABELS = {
  fr: ["Pas du tout d'accord", "Plutôt pas d'accord", "Neutre", "Plutôt d'accord", "Tout à fait d'accord"],
  en: ["Strongly disagree", "Somewhat disagree", "Neutral", "Somewhat agree", "Strongly agree"],
};

// What the scale displays: one single set at every viewport width (DP-26), sized
// for the 320px column, 7 characters per word at most. Labels that changed with
// the viewport would give two users different anchors, which is a difference of
// instrument between subjects (INV-18) — there is no long form above any width.
export const CHOICE_LABELS_SHORT = {
  fr: ["Pas du tout", "Plutôt pas", "Neutre", "Plutôt oui", "Tout à fait"],
  en: ["Not at all", "Rather not", "Neutral", "Rather yes", "Fully agree"],
};

// Keyed by the full formulation, because the scale component is handed the
// accessible labels and has no language of its own.
export const SHORT_LABEL = new Map(
  LANGS.flatMap((lang) => CHOICE_LABELS[lang].map((full, i) => [full, CHOICE_LABELS_SHORT[lang][i]])),
);

// The confidence scale, in words. The bounds live in score.js and only there
// (DP-11); these are the labels its level identifiers map to. A level is a word
// and never a shade, a tint or a graphic position (INV-12).
export const CONFIDENCE_LABELS = {
  fr: {
    none: "aucune comparaison",
    "very-low": "très faible",
    low: "faible",
    partial: "partielle",
  },
  en: {
    none: "no comparison",
    "very-low": "very low",
    low: "low",
    partial: "partial",
  },
};

export const THEMES = {
  fr: {
    economy: "Économie",
    social: "Social",
    ecology: "Écologie",
    institutions: "Institutions",
    security: "Sécurité",
    immigration: "Immigration",
    europe: "Europe",
    education: "Éducation",
    health: "Santé",
  },
  en: {
    economy: "Economy",
    social: "Welfare",
    ecology: "Environment",
    institutions: "Institutions",
    security: "Security",
    immigration: "Immigration",
    europe: "Europe",
    education: "Education",
    health: "Health",
  },
};

export const T = {
  fr: {
    title: "Civis",
    tagline: "Des propositions issues des programmes officiels. Sans étiquette, jusqu'à la fin.",
    // The questionnaire header (DP-27): five statements, in this order, 120
    // characters each at most — the length of the longest statement of the
    // fr-2027 corpus. The counts are passed in, never written here (K9).
    header: (proposals, formations) => [
      "Questionnaire à l'aveugle : positionnez-vous sur chaque proposition.",
      `${proposals} propositions tirées de documents de ${formations} formations, publiés en 2024, pour un scrutin de 2027.`,
      "Les énoncés sont nos reformulations des propositions, pas des citations.",
      "L'ordre est tiré au hasard dans le navigateur, non enregistré ; aucune formation n'est nommée avant la dernière réponse.",
      "Le questionnaire nécessite JavaScript pour enregistrer les réponses et calculer le résultat.",
    ],
    progress: (done, total) => `${done} réponse${done > 1 ? "s" : ""} sur ${total}`,
    skip: "Passer",
    submit: "Voir mes résultats",
    incomplete: "Répondez à au moins une question pour voir un résultat.",
    // The consent states a state, never a proposal (DP-04): the box is ticked,
    // so "add my answers" would let a hurried reader believe that doing nothing
    // refuses. The four statements that follow are what is sent, what is not,
    // why the shape of the exchange protects, and the residue we do not control
    // (DP-16, P2). No legal wording anywhere in them (I4).
    optout: "Vos réponses seront ajoutées aux statistiques publiques.",
    optoutRefusal: "Décocher n'envoie rien du tout.",
    optoutSent:
      "Ce qui part, une requête par réponse, avec pour seul contenu l'identifiant de la question et le rang de la réponse sur l'échelle :",
    optoutNotSent:
      "Ces deux champs sont tout ce que la requête contient : ni identifiant, ni horodatage, ni cookie, ni champ reliant deux réponses entre elles.",
    optoutWhy:
      "Les réponses partent une par une, dans un ordre tiré au hasard ; le serveur incrémente un compteur par question et par choix, et sa table n'a aucune colonne où deux réponses pourraient se rejoindre. L'onglet réseau du navigateur montre ce qui sort.",
    optoutIp:
      "Le serveur reçoit l'adresse IP de la requête, comme tout serveur. Son code ne l'enregistre pas ; ce que l'hébergeur en fait ne dépend pas de nous.",
    draftRestored:
      "Les réponses enregistrées dans cet onglet ont été restaurées, avec l'ordre des questions. Elles disparaissent à la fermeture de l'onglet.",
    draftClear: "Effacer mes réponses",
    results: "Vos résultats",
    // No result is withheld for want of answers (DP-19); this states the case
    // where nothing was compared, and names the action rather than the lack.
    noAnswers: "Aucune réponse non neutre enregistrée. Recommencer pour se positionner sur au moins une proposition.",
    restart: "Recommencer",
    // The result, as a fraction whose denominator sits inside the sentence
    // (DP-10, INV-13). The base decides the wording, so the sentence is written
    // whole here and read by its base; `{n}` is the agreed count, the one figure
    // the base does not determine. The plural rule stays in this file.
    resultFraction: (base) =>
      base === 0
        ? "Aucune réponse non neutre ne porte sur les propositions de ce programme."
        : `D'accord avec {n} sur ${base} proposition${base > 1 ? "s" : ""} comparée${base > 1 ? "s" : ""} dans ce programme.`,
    resultConfidence: (label, base) =>
      `Niveau de confiance : ${label}, sur ${base} proposition${base > 1 ? "s" : ""} comparée${base > 1 ? "s" : ""}.`,
    // Coverage is a property of the corpus, not of this passation (DP-12): it is
    // the same figure for every reader, and never the comparison base above.
    resultCoverage: (n, total) => `Couverture du corpus : ${n} des ${total} propositions du questionnaire.`,
    detail: "Le détail, question par question",
    sourceLabel: "Document officiel",
    // Provenance of the corpus, before the first figure (DP-28).
    sources: "Documents sources du corpus",
    published: (date) => `publié le ${date}`,
    publishedUnknown: "date de publication non indiquée",
    fingerprint: "SHA-256",
    // The aggregates. Every count here is a number of answers recorded for one
    // proposal — never a number of people, which the schema makes structurally
    // unknowable, and which a label claiming it would contradict in the very
    // words meant to illustrate it (DT-11, D6). Hence no "participants" and no
    // "personnes" anywhere below, heading included.
    //
    // Four messages, and they are not interchangeable: no service configured,
    // service that did not answer, no answer recorded, and the wait. A silent
    // disappearance is none of them (INV-14, P8).
    //
    // `{n}` is the one slot the script fills. The sentence takes no plural
    // agreement, so no plural rule travels to the client (D2).
    aggregate: "Compteurs de cette proposition",
    aggregateResponses: "Nombre de réponses enregistrées pour cette proposition : {n}",
    aggregatePercent: "{n} %",
    // The qualification, next to the figures and never elsewhere: it is what
    // makes the section admissible rather than an ornament on it (DP-15, P7).
    aggregateSample:
      "Échantillon auto-sélectionné, limité aux réponses laissées au comptage : ce n'est pas un sondage représentatif.",
    aggregatePending: "Compteurs en cours de chargement.",
    aggregateNoService: "Aucun service de compteurs n'est configuré pour ce déploiement.",
    aggregateUnavailable: "Le service de compteurs n'a pas répondu.",
    aggregateEmpty: "Aucune réponse enregistrée pour cette proposition.",
    yourAnswer: "Votre réponse",
    supports: "Défend cette mesure",
    opposes: "S'y oppose",
    backToTop: "Retour en haut",
    version: (commit, date) => `Version ${commit}, construite le ${date}`,
    versionLocal: "Build local : ni identifiant de commit, ni date de construction",
    repository: "Dépôt",
    quoteCheck: "Vérification des citations",
  },
  en: {
    title: "Civis",
    tagline: "Proposals taken from official manifestos. No labels until the end.",
    header: (proposals, formations) => [
      "Blind questionnaire: take a position on each proposal.",
      `${proposals} proposals taken from documents of ${formations} formations, published in 2024, for a 2027 election.`,
      "The statements are our reformulations of the proposals, not quotations.",
      "The order is drawn at random in the browser and is not recorded; no formation is named before the last answer.",
      "The questionnaire needs JavaScript to record the answers and compute the result.",
    ],
    progress: (done, total) => `${done} of ${total} answered`,
    skip: "Skip",
    submit: "See my results",
    incomplete: "Answer at least one question to get a result.",
    optout: "Your answers will be added to the public statistics.",
    optoutRefusal: "Unchecking sends nothing at all.",
    optoutSent:
      "What leaves, one request per answer, holding nothing but the question identifier and the rank of the answer on the scale:",
    optoutNotSent:
      "Those two fields are all the request holds: no identifier, no timestamp, no cookie, no field linking two answers together.",
    optoutWhy:
      "The answers leave one by one, in a random order; the server increments one counter per question and per choice, and its table has no column where two answers could meet. The browser's network tab shows what goes out.",
    optoutIp:
      "The server receives the request's IP address, as any server does. Its code does not record it; what the host does with it is not up to us.",
    draftRestored:
      "The answers stored in this tab have been restored, with the question order. They are dropped when the tab is closed.",
    draftClear: "Erase my answers",
    results: "Your results",
    noAnswers: "No non-neutral answer recorded. Start over to take a position on at least one proposal.",
    restart: "Start over",
    resultFraction: (base) =>
      base === 0
        ? "No non-neutral answer covers a proposal in this programme."
        : `Agreement with {n} of ${base} compared proposal${base > 1 ? "s" : ""} in this programme.`,
    resultConfidence: (label, base) =>
      `Confidence: ${label}, across ${base} compared proposal${base > 1 ? "s" : ""}.`,
    resultCoverage: (n, total) => `Corpus coverage: ${n} of the ${total} proposals in the questionnaire.`,
    detail: "Question by question",
    sourceLabel: "Official document",
    sources: "Source documents of the corpus",
    published: (date) => `published on ${date}`,
    publishedUnknown: "publication date not stated",
    fingerprint: "SHA-256",
    aggregate: "Counters for this proposal",
    aggregateResponses: "Answers recorded for this proposal: {n}",
    aggregatePercent: "{n}%",
    aggregateSample:
      "Self-selected sample, limited to the answers left to be counted: this is not a representative poll.",
    aggregatePending: "Counters loading.",
    aggregateNoService: "No counter service is configured for this deployment.",
    aggregateUnavailable: "The counter service did not answer.",
    aggregateEmpty: "No answer recorded for this proposal.",
    yourAnswer: "Your answer",
    supports: "Supports this measure",
    opposes: "Opposes it",
    backToTop: "Back to top",
    version: (commit, date) => `Version ${commit}, built on ${date}`,
    versionLocal: "Local build: no commit identifier, no build date",
    repository: "Repository",
    quoteCheck: "Quote verification",
  },
};
