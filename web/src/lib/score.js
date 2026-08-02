/**
 * Blind scoring, entirely client-side. No answer is ever sent anywhere to be
 * scored — the browser holds the only copy of a completed questionnaire.
 *
 * answers   { [questionId]: number in [-1, 1] }  missing or null = skipped
 * positions { [questionId]: [{ party, stance }] } stance is -1 or 1
 *
 * Returns one row per formation of the corpus, answered or not:
 *   { party, agreed, base, confidence }
 * `base` is the comparison base — proposals answered non-neutrally that this
 * formation holds a position on. `agreed` is how many of those go the same way
 * as the formation. The pair is a fraction, not a percentage: the corpus gives
 * denominators from 4 to 19, and a single number computed over four proposals
 * and one computed over nineteen are not the same measurement (DP-10).
 *
 * Intensity is dropped on purpose: "strongly agree" and "somewhat agree" count
 * the same. A nuance whose denominator moves between 4 and 19 is not a nuance.
 * Neutral and skipped answers reduce the base rather than counting against a
 * formation, which is exactly what they mean.
 *
 * Rows are sorted by fraction, and that order is a reading convenience — the
 * page marks no rank (DP-10).
 */
export function score(answers, positions) {
  // Every formation of the corpus gets a row before a single answer is read: a
  // formation with nothing to compare states its reason, it does not vanish
  // (INV-14). No minimum number of answers gates the computation (DP-19).
  const totals = new Map(
    Object.keys(coverage(positions)).map((party) => [party, { party, agreed: 0, base: 0 }]),
  );

  for (const [questionId, entries] of Object.entries(positions)) {
    const answer = answers[questionId];
    if (typeof answer !== "number" || answer === 0) continue;

    for (const { party, stance } of entries) {
      const total = totals.get(party);
      total.base += 1;
      if (Math.sign(answer) === stance) total.agreed += 1;
    }
  }

  return [...totals.values()]
    .map((total) => ({ ...total, confidence: confidence(total.base) }))
    .sort(
      // Cross-multiplied rather than divided: a base of zero has no fraction,
      // and NaN would sort unpredictably. Equal fractions fall back on the
      // larger base, which puts the uncomparable formations last.
      (a, b) => b.agreed * a.base - a.agreed * b.base || b.base - a.base,
    );
}

/**
 * Coverage: how many proposals of the questionnaire each formation holds a
 * position on. A property of the corpus, not of a passation — no answer takes
 * part, and the figure is the same for every reader (DP-12).
 *
 * Measured on fr-2027: nfp 19, rn 15, ensemble 10, lr 4, out of 30 proposals.
 */
export function coverage(positions) {
  const counts = {};
  for (const entries of Object.values(positions)) {
    for (const { party } of entries) counts[party] = (counts[party] ?? 0) + 1;
  }
  return counts;
}

/**
 * The confidence scale. This table is the only place its bounds exist: the
 * methodology page reads them from here rather than restating them, because a
 * threshold written twice diverges (DP-11).
 *
 * The bounds are not round numbers, they are coverage values measured in the
 * fr-2027 corpus. 4 is the coverage of the least covered formation (`lr`): at or
 * below it, the base is smaller than everything the corpus holds on one whole
 * formation. 10 is the coverage of the median formation (`ensemble`). 0 stands
 * alone because an absence displays as an absence (INV-14).
 *
 * The scale is capped: `partial` is its top and nothing sits above it, whatever
 * the base. A corpus this unbalanced supports no stronger claim — 19 comparisons
 * out of 19 do not either (DP-11).
 *
 * `max: null` is the open-ended step. Levels are identifiers, never displayed:
 * the words they map to live in ui.js.
 */
export const CONFIDENCE_LEVELS = [
  { level: "none", min: 0, max: 0 },
  { level: "very-low", min: 1, max: 4 },
  { level: "low", min: 5, max: 9 },
  { level: "partial", min: 10, max: null },
];

/** The confidence level for a comparison base. Same rule for every reader (INV-18). */
export function confidence(base) {
  return CONFIDENCE_LEVELS.find(({ max }) => max === null || base <= max).level;
}

/** Answer scale shared by the form and the aggregate counters. */
export const CHOICES = [-1, -0.5, 0, 0.5, 1];

/** Index into CHOICES, which is what the counter API stores. */
export function choiceIndex(value) {
  return CHOICES.indexOf(value);
}
