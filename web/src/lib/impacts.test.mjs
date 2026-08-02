// The all-or-nothing rule (DP-34, INV-22), and the real corpus it runs against.
//
// Two halves, on purpose. The fixtures below fix the behaviour case by case,
// including the one that matters — a question holding some entries but not all
// shows nothing at all. The corpus half then asserts the same property against
// the file that actually ships, so the rule is not merely correct in the
// abstract but correct on the content of the day.
//
// The corpus half deliberately asserts no list of question identifiers. PR-23
// fills the corpus wave by wave; a test naming today's two covered questions
// would have to be edited by every content PR, and a test edited by every
// content PR stops being read. What is asserted is what must hold at every
// wave: nothing partial is ever shown, and at least one question is.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { fullyAnalysed } from "./impacts.js";

const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const positions = read("../../../content/questions/fr-2027.positions.json");
const { impacts } = read("../../../content/impacts/fr-2027.json");

const entries = (...points) => points.map((point) => ({ point, stance: 1 }));
const analysed = (...points) => Object.fromEntries(points.map((point) => [point, { items: [] }]));

// --- The rule ----------------------------------------------------------------

test("a question shows its analyses when every position has an entry", () => {
  assert.equal(fullyAnalysed(entries("a", "b", "c"), analysed("a", "b", "c")), true);
  assert.equal(fullyAnalysed(entries("a"), analysed("a")), true);
});

// The case DP-34 exists for, and the one a naive implementation gets wrong: the
// entry for "a" is reviewed, complete and ready, and it is not shown, because
// showing it beside two positions with nothing would make it the documented one.
test("a question with some entries but not all shows none of them", () => {
  assert.equal(fullyAnalysed(entries("a", "b", "c"), analysed("a")), false);
  assert.equal(fullyAnalysed(entries("a", "b", "c"), analysed("a", "b")), false);
  assert.equal(fullyAnalysed(entries("a", "b"), analysed("b")), false);
});

test("a question with no entry at all shows nothing", () => {
  assert.equal(fullyAnalysed(entries("a", "b"), {}), false);
});

// A question with no position renders no list item, so there is nothing to
// attach an analysis to. It answers no rather than vacuously yes: `every` on an
// empty array is true, and this is the one place the rule could report a
// question as analysed while it displays nothing at all.
test("a question with no position is not analysed", () => {
  assert.equal(fullyAnalysed([], analysed("a")), false);
  assert.equal(fullyAnalysed([], {}), false);
});

// The prototype chain is not the content file.
test("an inherited property is not an analysis", () => {
  assert.equal(fullyAnalysed(entries("constructor"), {}), false);
  assert.equal(fullyAnalysed(entries("toString"), {}), false);
});

// What PR-23 does, wave after wave: completing the last missing position of a
// question flips it on, and flips on nothing else. This is the whole ramp-up
// behaviour, and it is a property of the rule rather than of the corpus.
test("completing the last position of a question is what makes it visible", () => {
  const question = entries("a", "b", "c");
  assert.equal(fullyAnalysed(question, analysed("a", "b")), false);
  assert.equal(fullyAnalysed(question, analysed("a", "b", "c")), true);
  // A neighbouring question, untouched by that wave, is unaffected.
  assert.equal(fullyAnalysed(entries("d", "e"), analysed("a", "b", "c", "d")), false);
});

// --- The corpus that ships ---------------------------------------------------

test("no question of the corpus can display a partial analysis", () => {
  for (const [id, entry] of Object.entries(positions)) {
    if (!fullyAnalysed(entry, impacts)) continue;
    const missing = entry.filter((position) => !Object.hasOwn(impacts, position.point));
    assert.deepEqual(missing, [], `${id} is shown with ${missing.length} position(s) unanalysed`);
  }
});

// The corollary, and the one that catches a rule inverted or short-circuited: a
// question holding at least one entry without holding them all must be silent.
test("every partially analysed question of the corpus is silent", () => {
  for (const [id, entry] of Object.entries(positions)) {
    const held = entry.filter((position) => Object.hasOwn(impacts, position.point)).length;
    if (held === 0 || held === entry.length) continue;
    const shown = `${held} of ${entry.length} positions`;
    assert.equal(fullyAnalysed(entry, impacts), false, `${id} shows ${shown}`);
  }
});

// The pilot is delivered, so something is displayed. Without this the two tests
// above are satisfied by a rule that always answers no.
test("the corpus displays at least one question", () => {
  const shown = Object.entries(positions).filter(([, entry]) => fullyAnalysed(entry, impacts));
  assert.ok(shown.length > 0, "no question of the corpus displays an analysis");
  console.log(`analyses displayed on ${shown.length} of ${Object.keys(positions).length} questions`);
});
