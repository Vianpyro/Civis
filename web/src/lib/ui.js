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
    intro:
      "Positionnez-vous sur chaque proposition. Aucun parti n'est nommé avant la dernière réponse, et aucune statistique n'est affichée pendant le questionnaire : les deux réintroduiraient le biais que cet outil sert à supprimer.",
    progress: (done, total) => `${done} réponse${done > 1 ? "s" : ""} sur ${total}`,
    skip: "Passer",
    submit: "Voir mes résultats",
    incomplete: "Répondez à au moins une question pour voir un résultat.",
    optout: "Ajouter mes réponses aux statistiques publiques",
    optoutHelp:
      "Chaque réponse est envoyée séparément, sans identifiant, sans horodatage et sans lien avec les autres. Décocher n'envoie rien du tout.",
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
    intro:
      "Take a position on each proposal. No party is named before your last answer, and no statistics are shown during the questionnaire: either would reintroduce the bias this tool exists to remove.",
    progress: (done, total) => `${done} of ${total} answered`,
    skip: "Skip",
    submit: "See my results",
    incomplete: "Answer at least one question to get a result.",
    optout: "Add my answers to the public statistics",
    optoutHelp:
      "Each answer is sent separately, with no identifier, no timestamp and no link to the others. Unchecking sends nothing at all.",
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
