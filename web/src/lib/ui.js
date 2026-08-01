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
    optout: "Ajouter mes réponses aux statistiques publiques",
    optoutHelp:
      "Chaque réponse est envoyée séparément, sans identifiant, sans horodatage et sans lien avec les autres. Décocher n'envoie rien du tout.",
    draftRestored:
      "Les réponses enregistrées dans cet onglet ont été restaurées, avec l'ordre des questions. Elles disparaissent à la fermeture de l'onglet.",
    draftClear: "Effacer mes réponses",
    results: "Vos résultats",
    noAnswers: "Aucune réponse enregistrée.",
    restart: "Recommencer",
    agreement: "d'accord",
    matched: (n) => `sur ${n} question${n > 1 ? "s" : ""} comparable${n > 1 ? "s" : ""}`,
    detail: "Le détail, question par question",
    sourceLabel: "Document officiel",
    aggregate: "Réponses des autres participants",
    aggregateEmpty: "Pas encore de statistiques agrégées.",
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
    optout: "Add my answers to the public statistics",
    optoutHelp:
      "Each answer is sent separately, with no identifier, no timestamp and no link to the others. Unchecking sends nothing at all.",
    draftRestored:
      "The answers stored in this tab have been restored, with the question order. They are dropped when the tab is closed.",
    draftClear: "Erase my answers",
    results: "Your results",
    noAnswers: "No answers recorded.",
    restart: "Start over",
    agreement: "agreement",
    matched: (n) => `across ${n} comparable question${n > 1 ? "s" : ""}`,
    detail: "Question by question",
    sourceLabel: "Official document",
    aggregate: "How others answered",
    aggregateEmpty: "No aggregate statistics yet.",
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
