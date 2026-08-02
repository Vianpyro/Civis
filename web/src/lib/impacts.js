// All or nothing, by question (DP-34, INV-22).
//
// A question shows its analyses only if every one of its positions has a
// reviewed entry. Short of that it shows none — including for the positions that
// do have one. The reader compares the positions of a question side by side, and
// the one carrying an analysis would look documented against the ones carrying
// none: an asymmetry inside the unit of comparison, which no notice compensates
// for. Hiding ready content is a real cost and it is accepted.
//
// The rule lives here rather than inline in results.astro so that it can be run
// without a browser and without a build. It is the one piece of product logic
// this feature adds, it decides what thirty questions do or do not display, and
// its two failure modes are silent: a question that shows nothing when it should
// show something is invisible, and a question that shows a partial analysis is
// the exact bias DP-34 exists to prevent. impacts.test.mjs holds both.
//
// `Object.hasOwn` rather than `in` or a truthiness test: `in` walks the
// prototype chain, so a point identified as "constructor" or "toString" would
// count as analysed against an empty file.
export const fullyAnalysed = (entries, impacts) =>
  entries.length > 0 && entries.every((entry) => Object.hasOwn(impacts, entry.point));
