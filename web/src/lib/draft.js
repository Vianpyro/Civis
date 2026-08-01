/**
 * The questionnaire draft: answers in progress and the order they are displayed
 * in (DP-09, DT-09).
 *
 * `sessionStorage` only, never `localStorage`: the trace dies with the tab. The
 * key is the one the submission already writes and the results page already
 * reads, so the draft creates no new data, no new key and no new lifetime.
 *
 * Compatibility with that read is a hard constraint. The results page parses the
 * key as `{ questionId: number }` and keeps the entries whose value is a number.
 * The order therefore travels inside the same object, under a key that is not a
 * question id and whose value is not a number: the existing read walks past it.
 *
 * The order is also what makes a stored object a draft. A submission writes the
 * answers alone — the payload handed to the results page survives, the draft
 * does not, and coming back to the questionnaire restores nothing.
 */

/** The key the submission and the results page already use. */
export const DRAFT_KEY = "civis:answers";

/** Question ids are `q-…`, so this can never collide with one. */
export const ORDER_KEY = "civis:order";

/**
 * @param answers { [questionId]: number } — values from the answer scale
 * @param order   [questionId] in display order
 */
export function toDraft(answers, order) {
  return { ...answers, [ORDER_KEY]: order };
}

/** { answers, order }, or null when the stored object carries no order. */
export function fromDraft(stored) {
  const order = stored?.[ORDER_KEY];
  if (!Array.isArray(order)) return null;
  return {
    // The same rule the results page applies: an answer is a numeric entry.
    answers: Object.fromEntries(
      Object.entries(stored).filter(([, value]) => typeof value === "number"),
    ),
    order,
  };
}
