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

    // --- Methodology page (PR-13) --------------------------------------------
    //
    // Documentation, not a landing (DP-07): no lead, no action button, no claim
    // about the project's own qualities. Every sentence that states a property
    // names the gesture that would contradict it (P1).
    //
    // No figure of the corpus and no threshold is written here. Coverage counts
    // arrive as arguments, confidence bounds and the percentage threshold come
    // from score.js: a value restated in this file would diverge from the code
    // silently, and this is the page that would then be asserting a rule the
    // product does not apply (K9, D7).
    methodology: "Méthodologie",
    methodIntro:
      "Cette page est notre commentaire sur l'instrument : ce qu'il contient, comment il a été fabriqué, et ce qu'il ne permet pas de conclure. Elle ne cite aucun document officiel ; les citations sont sur la page de résultats, chacune avec son document et son empreinte.",

    // The limits come first, not last: a defect stated by the instrument is a
    // documented characteristic, the same defect found by a reader is a proof of
    // duplicity (P5, DP-13). Two of the sentences below already exist in this
    // file, next to the counters and the consent, and are read from there rather
    // than written a second time.
    methodLimits: "Limites connues",
    methodLimitsDating:
      "Les documents du corpus ont été publiés en 2024, pour les élections législatives ; le questionnaire porte sur le scrutin de 2027, dont les programmes ne sont pas parus.",
    methodLimitsFetchDate:
      "La date à laquelle chaque document a été téléchargé n'est enregistrée nulle part : le dépôt ne conserve que la date de publication annoncée par le document lui-même.",
    methodLimitsVersioning:
      "Les énoncés ne portent ni numéro de version ni date. Une reformulation ne laisse de trace que dans l'historique git, et des compteurs peuvent donc porter sur deux formulations sous un même identifiant.",
    methodCoverageTitle: "Propositions retenues par formation",
    methodCoverageColumn: "Formation",
    methodCoverageCount: "Propositions retenues",
    methodCoverageValue: (n, total) => `${n} sur ${total}`,
    methodCoverageNote:
      "Une formation peu couverte et une formation très couverte ne sont pas comparées sur la même base. C'est pourquoi chaque résultat porte le nombre de propositions comparées dans sa phrase, et non un pourcentage.",
    methodSingleParty: (n, total) =>
      `${n} des ${total} questions ne concernent qu'une seule formation : y répondre fait monter cette formation sans rien retirer aux autres. Le résultat dépend donc de la composition du corpus, pas seulement des réponses.`,

    methodCorpus: "Le corpus",
    methodCorpusIntro: (proposals, formations) =>
      `Le questionnaire porte ${proposals} énoncés, tirés de documents publiés par ${formations} formations. Les documents lus sont ceux-ci, avec leur date de publication et l'empreinte SHA-256 du fichier récupéré :`,
    methodCorpusCheck:
      "Chaque citation est cherchée mot pour mot dans le document que sa source déclare, à chaque construction du site ; la construction échoue si elle ne s'y trouve pas. Hors ligne, la vérification est signalée comme sautée, jamais tenue pour faite. Télécharger un document ci-dessus et calculer son SHA-256 redonne l'empreinte affichée, ou la contredit.",

    methodStatements: "Les énoncés",
    methodStatementsEditorial:
      "Les énoncés du questionnaire sont nos reformulations des propositions, écrites en questions fermées et parfois traduites. Ce ne sont pas des citations. La citation d'origine et son document figurent sous chaque question, sur la page de résultats : les comparer est ce qui met une reformulation en défaut.",

    // The four facts, in this order and no other (DP-17). The most alarming one
    // comes first, which is what makes the three that follow credible; the
    // reverse order would read as a justification. No mitigating formula.
    methodModel: "Rôle du modèle de langage",
    methodModelFacts: [
      "Les brouillons des énoncés sont générés par un modèle de langage, hors ligne et en lot, avant toute entrée dans le dépôt.",
      "Chaque brouillon est relu par une personne avant d'entrer dans le contenu. Rien n'entre sans cette relecture.",
      "Aucun appel à un modèle de langage n'a lieu pendant l'exécution du site : ni au chargement, ni pendant le questionnaire, ni au calcul du résultat. L'onglet réseau du navigateur montre ce qui sort.",
      "Les citations rattachées aux propositions sont vérifiées mot pour mot par un programme, à chaque construction du site.",
    ],

    methodPassation: "La passation",
    methodOrder:
      "L'ordre des questions est tiré au hasard dans le navigateur, à chaque ouverture. Le tirage n'est envoyé nulle part ; il est conservé avec le brouillon dans l'onglet, pour qu'une restauration retrouve l'ordre affiché, et disparaît à la fermeture de l'onglet. Recharger la page change l'ordre.",
    methodLabels:
      "L'échelle porte cinq positions, avec les mêmes libellés à toutes les largeurs d'écran : des libellés qui changeraient avec la largeur donneraient des repères différents selon l'appareil. Le libellé affiché est abrégé pour tenir dans une colonne à 320 px ; le nom restitué par un lecteur d'écran reste la formulation complète.",
    methodLabelDisplayed: "Libellé affiché",
    methodLabelAccessible: "Nom accessible",
    methodNeutral:
      "« Neutre » et « Passer » sont traités à l'identique par le calcul : dans les deux cas la question sort de la base de comparaison. La distinction ne porte que sur les compteurs publics — une réponse « Neutre » y est enregistrée, une question passée n'envoie rien — parce que n'avoir pas d'avis et se situer au milieu de l'axe ne sont pas la même réponse.",

    methodCalculation: "Le calcul",
    methodFraction:
      "Le résultat d'une formation est une fraction : le nombre de propositions sur lesquelles la réponse va dans le même sens que la formation, sur le nombre de propositions comparées. Ni pourcentage, ni barre, ni rang. L'intensité n'est pas pondérée : « Tout à fait » et « Plutôt oui » comptent l'un et l'autre pour un accord.",
    methodBase:
      "La base de comparaison est le nombre de propositions sur lesquelles la réponse n'est pas neutre et sur lesquelles la formation a une position identifiée. Les réponses neutres et les questions passées la réduisent, ce qui est exactement leur sens.",
    methodCoverageDefinition:
      "La couverture est autre chose : c'est une propriété du corpus, le nombre de propositions du questionnaire sur lesquelles une formation a une position, indépendamment des réponses. C'est le tableau donné plus haut, et il est le même pour tout le monde.",
    methodConfidence:
      "Le niveau de confiance se lit sur la base de comparaison, selon cette table. C'est un mot, jamais une nuance ni une position graphique. L'échelle est plafonnée : aucun palier n'existe au-dessus du dernier, quelle que soit la base — un corpus aussi déséquilibré n'en soutient pas.",
    methodConfidenceBase: "Base de comparaison",
    methodConfidenceLevel: "Niveau affiché",
    methodConfidenceRange: (min, max) =>
      max === null ? `${min} ou plus` : min === max ? `${min}` : `${min} à ${max}`,
    methodPercent: (n) =>
      `Les compteurs d'une proposition sont affichés en pourcentages à partir de ${n} réponses enregistrées pour cette proposition, et en effectifs bruts en deçà. Les pourcentages sont arrondis à l'unité, ce qui annonce une précision d'un point ; sous ${n} réponses, une réponse de plus en déplace la valeur de davantage.`,

    // A named person, dated. Admissible against P1 because it is falsifiable by
    // contradiction: it commits someone who can be shown to be wrong (P6).
    methodEditorial: "Responsable éditorial et déclaration d'intérêts",
    methodEditorialWho:
      "Le dépôt est écrit et maintenu par une seule personne, Vianpyro (github.com/Vianpyro). Le choix des propositions retenues, la rédaction des énoncés et la relecture des brouillons lui incombent.",
    methodEditorialInterests:
      "Le projet ne reçoit aucun financement et n'a été commandé par personne. Son responsable éditorial n'adhère à aucune formation politique et n'est rémunéré par aucune. Cette déclaration nomme quelqu'un : elle se contredit par la production d'un fait contraire.",
    methodEditorialDate: "Déclaration du 1er août 2026.",

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

    // --- Methodology page (PR-13) --------------------------------------------
    methodology: "Methodology",
    methodIntro:
      "This page is our commentary on the instrument: what it holds, how it was made, and what it does not let anyone conclude. It quotes no official document; the quotations are on the results page, each with its document and its fingerprint.",

    methodLimits: "Known limits",
    methodLimitsDating:
      "The documents of the corpus were published in 2024, for the legislative elections; the questionnaire covers the 2027 election, whose manifestos are not out.",
    methodLimitsFetchDate:
      "The date each document was downloaded is recorded nowhere: the repository keeps only the publication date the document itself states.",
    methodLimitsVersioning:
      "The statements carry neither a version number nor a date. A rewording leaves no trace outside the git history, so counters may cover two formulations under one identifier.",
    methodCoverageTitle: "Proposals taken from each formation",
    methodCoverageColumn: "Formation",
    methodCoverageCount: "Proposals taken",
    methodCoverageValue: (n, total) => `${n} of ${total}`,
    methodCoverageNote:
      "A thinly covered formation and a heavily covered one are not compared on the same base. That is why every result carries the number of compared proposals inside its sentence, and not a percentage.",
    methodSingleParty: (n, total) =>
      `${n} of the ${total} questions concern a single formation: answering them raises that formation without taking anything from the others. The result therefore depends on how the corpus is made up, not on the answers alone.`,

    methodCorpus: "The corpus",
    methodCorpusIntro: (proposals, formations) =>
      `The questionnaire holds ${proposals} statements, taken from documents published by ${formations} formations. These are the documents read, with their publication date and the SHA-256 fingerprint of the file retrieved:`,
    methodCorpusCheck:
      "Every quotation is looked for word for word in the document its source states, at every build of the site; the build fails if it is not there. Offline, the check is reported as skipped, never taken as done. Downloading a document above and computing its SHA-256 gives back the fingerprint shown, or contradicts it.",

    methodStatements: "The statements",
    methodStatementsEditorial:
      "The statements of the questionnaire are our reformulations of the proposals, written as closed questions and sometimes translated. They are not quotations. The original quotation and its document sit under each question on the results page: comparing them is what catches a reformulation out.",

    methodModel: "Role of the language model",
    methodModelFacts: [
      "Draft statements are generated by a language model, offline and in batches, before anything enters the repository.",
      "Every draft is read by a person before it enters the content. Nothing enters without that review.",
      "No language model is called while the site runs: not on load, not during the questionnaire, not when the result is computed. The browser's network tab shows what goes out.",
      "The quotations attached to the proposals are checked word for word by a program, at every build of the site.",
    ],

    methodPassation: "Taking the questionnaire",
    methodOrder:
      "The order of the questions is drawn at random in the browser, at every opening. The draw is sent nowhere; it is kept with the draft inside the tab, so that a restoration finds the order that was displayed, and it is dropped when the tab is closed. Reloading the page changes the order.",
    methodLabels:
      "The scale holds five positions, with the same labels at every screen width: labels that changed with the width would give different anchors depending on the device. The displayed label is abridged to fit a column at 320px; the name a screen reader gives back stays the full formulation.",
    methodLabelDisplayed: "Displayed label",
    methodLabelAccessible: "Accessible name",
    methodNeutral:
      "“Neutral” and “Skip” are treated the same way by the computation: either one takes the question out of the comparison base. The distinction bears on the public counters alone — a “Neutral” answer is recorded there, a skipped question sends nothing — because holding no view and sitting at the middle of the axis are not the same answer.",

    methodCalculation: "The computation",
    methodFraction:
      "The result of a formation is a fraction: the number of proposals where the answer goes the same way as the formation, over the number of proposals compared. No percentage, no bar, no rank. Intensity is not weighted: “Fully agree” and “Rather yes” both count as agreement.",
    methodBase:
      "The comparison base is the number of proposals where the answer is not neutral and where the formation holds an identified position. Neutral answers and skipped questions reduce it, which is exactly what they mean.",
    methodCoverageDefinition:
      "Coverage is another thing: a property of the corpus, the number of proposals of the questionnaire a formation holds a position on, independently of any answer. That is the table given above, and it is the same for every reader.",
    methodConfidence:
      "The confidence level is read from the comparison base, according to this table. It is a word, never a shade or a graphic position. The scale is capped: no step exists above the last one, whatever the base — a corpus this unbalanced supports none.",
    methodConfidenceBase: "Comparison base",
    methodConfidenceLevel: "Level displayed",
    methodConfidenceRange: (min, max) =>
      max === null ? `${min} or more` : min === max ? `${min}` : `${min} to ${max}`,
    methodPercent: (n) =>
      `The counters of a proposal are shown as percentages from ${n} answers recorded for that proposal onwards, and as raw counts below it. Percentages are rounded to the unit, which announces a precision of one point; below ${n} answers, one more answer moves the value by more than that.`,

    methodEditorial: "Editorial responsibility and declaration of interests",
    methodEditorialWho:
      "The repository is written and maintained by one person, Vianpyro (github.com/Vianpyro). The choice of the proposals kept, the writing of the statements and the review of the drafts are theirs.",
    methodEditorialInterests:
      "The project receives no funding and was commissioned by no one. Its editorial lead belongs to no political formation and is paid by none. This declaration names someone: it is contradicted by producing a fact against it.",
    methodEditorialDate: "Declared on 1 August 2026.",

    version: (commit, date) => `Version ${commit}, built on ${date}`,
    versionLocal: "Local build: no commit identifier, no build date",
    repository: "Repository",
    quoteCheck: "Quote verification",
  },
};
