/**
 * Blind scoring, entirely client-side. No answer is ever sent anywhere to be
 * scored — the browser holds the only copy of a completed questionnaire.
 *
 * answers   { [questionId]: number in [-1, 1] }  missing or null = skipped
 * positions { [questionId]: [{ party, stance }] } stance is -1 or 1
 *
 * Returns [{ party, agreement, matched }] sorted by agreement, descending.
 * `agreement` is in [0, 1]; `matched` is how many questions actually compared.
 */
export function score(answers, positions) {
  const totals = new Map();

  for (const [questionId, entries] of Object.entries(positions)) {
    const answer = answers[questionId];
    if (typeof answer !== "number" || answer === 0) continue;

    for (const { party, stance } of entries) {
      const total = totals.get(party) ?? { party, sum: 0, weight: 0, matched: 0 };
      total.sum += answer * stance;
      total.weight += Math.abs(answer);
      total.matched += 1;
      totals.set(party, total);
    }
  }

  return [...totals.values()]
    .map(({ party, sum, weight, matched }) => ({
      party,
      // Map [-weight, +weight] onto [0, 1] so parties answered on different
      // numbers of questions stay comparable.
      agreement: (sum / weight + 1) / 2,
      matched,
    }))
    .sort((a, b) => b.agreement - a.agreement || b.matched - a.matched);
}

/** Answer scale shared by the form and the aggregate counters. */
export const CHOICES = [-1, -0.5, 0, 0.5, 1];

/** Index into CHOICES, which is what the counter API stores. */
export function choiceIndex(value) {
  return CHOICES.indexOf(value);
}
