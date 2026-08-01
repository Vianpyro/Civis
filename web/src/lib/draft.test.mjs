import assert from "node:assert/strict";
import { test } from "node:test";

import { DRAFT_KEY, ORDER_KEY, fromDraft, toDraft } from "./draft.js";

const answers = { "q-isf": 1, "q-smic": -0.5, "q-succession": 0 };
const order = ["q-smic", "q-succession", "q-isf"];

// The stored value goes through JSON, so the round trip is tested through it.
const stored = (value) => JSON.parse(JSON.stringify(value));

test("a draft round-trips answers and drawn order", () => {
  const back = fromDraft(stored(toDraft(answers, order)));
  assert.deepEqual(back.answers, answers);
  assert.deepEqual(back.order, order, "the order restored is the order stored");
});

test("the order is invisible to the read the results page makes", () => {
  const draft = stored(toDraft(answers, order));
  // How results.astro reads the key: the entries whose value is a number.
  const asRead = Object.fromEntries(
    Object.entries(draft).filter(([, value]) => typeof value === "number"),
  );
  assert.deepEqual(asRead, answers, "the payload is exactly the answers");
  assert.equal(asRead[ORDER_KEY], undefined);
  assert.equal(DRAFT_KEY, "civis:answers", "the key stays the one already in use");
});

test("a submission payload is not a draft", () => {
  assert.equal(fromDraft(stored(answers)), null, "answers without an order restore nothing");
  assert.equal(fromDraft(null), null);
  assert.equal(fromDraft({}), null);
});

test("a draft with no answer yet still carries its order", () => {
  const back = fromDraft(stored(toDraft({}, order)));
  assert.deepEqual(back.answers, {});
  assert.deepEqual(back.order, order);
});
