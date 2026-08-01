import assert from "node:assert/strict";
import { test } from "node:test";

import { CHOICES, choiceIndex, score } from "./score.js";

const positions = {
  q1: [
    { party: "a", stance: 1 },
    { party: "b", stance: -1 },
  ],
  q2: [{ party: "a", stance: 1 }],
  q3: [{ party: "b", stance: 1 }],
};

const by = (rows, party) => rows.find((row) => row.party === party);

test("full agreement is 1, full disagreement is 0", () => {
  const rows = score({ q1: 1, q2: 1, q3: -1 }, positions);
  assert.equal(by(rows, "a").agreement, 1);
  assert.equal(by(rows, "b").agreement, 0);
  assert.equal(rows[0].party, "a", "ranked by agreement");
});

test("opposite answers flip the ranking", () => {
  const rows = score({ q1: -1, q2: -1, q3: 1 }, positions);
  assert.equal(by(rows, "a").agreement, 0);
  assert.equal(by(rows, "b").agreement, 1);
});

test("half-strength answers agree fully but count less", () => {
  const rows = score({ q1: 0.5 }, positions);
  assert.equal(by(rows, "a").agreement, 1, "direction, not magnitude, drives agreement");
  assert.equal(by(rows, "a").matched, 1);
});

test("one for, one against lands at the midpoint", () => {
  const rows = score({ q1: 1, q2: -1 }, positions);
  assert.equal(by(rows, "a").agreement, 0.5);
});

test("neutral and skipped answers are excluded, not counted as disagreement", () => {
  assert.deepEqual(score({ q1: 0 }, positions), []);
  assert.deepEqual(score({ q1: null }, positions), []);
  assert.deepEqual(score({}, positions), []);
  assert.equal(by(score({ q1: 1, q2: 0 }, positions), "a").matched, 1);
});

test("a party is only scored on questions it has a position on", () => {
  const rows = score({ q2: 1 }, positions);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].party, "a");
});

test("the answer scale round-trips through the counter index", () => {
  for (const value of CHOICES) {
    assert.equal(CHOICES[choiceIndex(value)], value);
  }
  assert.equal(choiceIndex(0.25), -1, "an off-scale value is not a valid choice");
});
