import assert from "node:assert/strict";
import { test } from "node:test";

import { CHOICES, CONFIDENCE_LEVELS, choiceIndex, confidence, coverage, score } from "./score.js";

const positions = {
  q1: [
    { party: "a", stance: 1 },
    { party: "b", stance: -1 },
  ],
  q2: [{ party: "a", stance: 1 }],
  q3: [{ party: "b", stance: 1 }],
};

const by = (rows, party) => rows.find((row) => row.party === party);

// A corpus with one formation holding `n` positions, one per question, so a test
// can drive a comparison base to an exact value.
const corpusOf = (n) =>
  Object.fromEntries(Array.from({ length: n }, (_, i) => [`q${i}`, [{ party: "a", stance: 1 }]]));
const answersFor = (n, value = 1) =>
  Object.fromEntries(Array.from({ length: n }, (_, i) => [`q${i}`, value]));

// The base a passation of `n` non-neutral answers actually produces, so a bound
// is asserted against a real run of score() and not only against the rule.
const baseOf = (n) => by(score(answersFor(n), corpusOf(Math.max(n, 1))), "a").base;

// --- the fraction ------------------------------------------------------------

test("full agreement is the whole base, full disagreement is none of it", () => {
  const rows = score({ q1: 1, q2: 1, q3: -1 }, positions);
  assert.deepEqual({ agreed: by(rows, "a").agreed, base: by(rows, "a").base }, { agreed: 2, base: 2 });
  assert.deepEqual({ agreed: by(rows, "b").agreed, base: by(rows, "b").base }, { agreed: 0, base: 2 });
  assert.equal(rows[0].party, "a", "ordered by fraction");
});

test("opposite answers flip the order", () => {
  const rows = score({ q1: -1, q2: -1, q3: 1 }, positions);
  assert.equal(by(rows, "a").agreed, 0);
  assert.equal(by(rows, "b").agreed, 2);
  assert.equal(rows[0].party, "b");
});

test("a mixed passation gives a mixed fraction", () => {
  const rows = score({ q1: 1, q2: -1 }, positions);
  assert.deepEqual({ agreed: by(rows, "a").agreed, base: by(rows, "a").base }, { agreed: 1, base: 2 });
});

test("intensity is dropped: half-strength counts exactly like full strength", () => {
  const half = score({ q1: 0.5, q2: 1 }, positions);
  const full = score({ q1: 1, q2: 1 }, positions);
  assert.deepEqual(by(half, "a"), by(full, "a"));
});

test("neutral and skipped answers reduce the base, they are not disagreement", () => {
  const rows = score({ q1: 1, q2: 0 }, positions);
  assert.deepEqual({ agreed: by(rows, "a").agreed, base: by(rows, "a").base }, { agreed: 1, base: 1 });
  assert.equal(by(score({ q1: 1, q2: null }, positions), "a").base, 1);
  assert.equal(by(score({ q1: 1 }, positions), "a").base, 1);
});

test("a formation is only compared on questions it has a position on", () => {
  const rows = score({ q2: 1 }, positions);
  assert.equal(by(rows, "a").base, 1);
  assert.equal(by(rows, "b").base, 0, "b holds no position on q2");
});

// --- absences ----------------------------------------------------------------

test("a formation with nothing compared is still a row, with a base of zero", () => {
  const rows = score({ q2: 1 }, positions);
  assert.equal(rows.length, 2, "every formation of the corpus is returned");
  assert.deepEqual(by(rows, "b"), { party: "b", agreed: 0, base: 0, confidence: "none" });
  assert.equal(rows.at(-1).party, "b", "an uncomparable formation sorts last, it is not dropped");
});

test("zero answers still returns every formation", () => {
  const rows = score({}, positions);
  assert.equal(rows.length, 2);
  assert.deepEqual(
    rows.map((row) => [row.base, row.confidence]),
    [
      [0, "none"],
      [0, "none"],
    ],
  );
});

test("answers that are all neutral compare nothing", () => {
  const rows = score({ q1: 0, q2: 0, q3: 0 }, positions);
  assert.ok(
    rows.every((row) => row.base === 0 && row.agreed === 0),
    "neutral is not a position, so there is nothing to compare",
  );
});

test("no figure is ever NaN, whatever the answers", () => {
  for (const answers of [{}, { q1: 0 }, { q1: null }, { q1: 1 }]) {
    for (const row of score(answers, positions)) {
      assert.ok(Number.isInteger(row.agreed) && Number.isInteger(row.base), JSON.stringify(row));
    }
  }
});

// --- coverage ----------------------------------------------------------------

test("coverage counts the corpus, and no answer takes part in it", () => {
  assert.deepEqual(coverage(positions), { a: 2, b: 2 });
});

test("coverage is the same figure for every passation", () => {
  const reference = coverage(positions);
  for (const answers of [{}, { q1: 1 }, { q1: -1, q2: 0, q3: 1 }]) {
    score(answers, positions);
    assert.deepEqual(coverage(positions), reference);
  }
});

// --- the confidence scale ----------------------------------------------------
//
// One test per bound of DP-11. This is where an off-by-one comparison — `<`
// where `<=` belongs — passes unnoticed, so each bound is asserted on its own
// value and not on a value inside the range.

test("base 0 is a state, not a level", () => {
  assert.equal(confidence(0), "none");
  assert.equal(baseOf(0), 0);
});

test("base 1 is the bottom of the scale", () => {
  assert.equal(confidence(1), "very-low");
  assert.equal(confidence(baseOf(1)), "very-low");
});

test("base 4 is still very low — the coverage of lr, the least covered formation", () => {
  assert.equal(confidence(4), "very-low");
  assert.equal(confidence(baseOf(4)), "very-low");
});

test("base 5 is low", () => {
  assert.equal(confidence(5), "low");
  assert.equal(confidence(baseOf(5)), "low");
});

test("base 9 is still low", () => {
  assert.equal(confidence(9), "low");
  assert.equal(confidence(baseOf(9)), "low");
});

test("base 10 is partial — the coverage of ensemble, the median formation", () => {
  assert.equal(confidence(10), "partial");
  assert.equal(confidence(baseOf(10)), "partial");
});

test("the scale is capped: 19 out of 19 is still partial", () => {
  assert.equal(confidence(19), "partial", "19 is the largest coverage of the fr-2027 corpus");
  assert.equal(confidence(baseOf(19)), "partial");
  assert.equal(confidence(30), "partial", "and nothing above it opens a new step");
});

test("the published bounds are 0 / 1-4 / 5-9 / >= 10 and nothing else", () => {
  assert.deepEqual(CONFIDENCE_LEVELS, [
    { level: "none", min: 0, max: 0 },
    { level: "very-low", min: 1, max: 4 },
    { level: "low", min: 5, max: 9 },
    { level: "partial", min: 10, max: null },
  ]);
  // The table is what the methodology page publishes, so it must describe the
  // function exactly: every declared range answers with its own level, and the
  // steps leave no gap between them (DP-11, D7).
  for (const [i, { level, min, max }] of CONFIDENCE_LEVELS.entries()) {
    assert.equal(confidence(min), level);
    if (max !== null) {
      assert.equal(confidence(max), level);
      assert.equal(CONFIDENCE_LEVELS[i + 1].min, max + 1, "no gap between steps");
    }
  }
});

test("every level a row carries comes from the published table", () => {
  const levels = CONFIDENCE_LEVELS.map(({ level }) => level);
  for (const row of score({ q1: 1, q2: 1 }, positions)) {
    assert.ok(levels.includes(row.confidence));
  }
});

// --- the answer scale --------------------------------------------------------

test("the answer scale round-trips through the counter index", () => {
  for (const value of CHOICES) {
    assert.equal(CHOICES[choiceIndex(value)], value);
  }
  assert.equal(choiceIndex(0.25), -1, "an off-scale value is not a valid choice");
});
