// Key parity of the interface strings (PR-14).
//
// Every table of ui.js is keyed by language, and a key present in one language
// and missing in the other produces an empty node or `undefined` on one side of
// the site only. Nothing else in the product reports it: the build succeeds, the
// blindness guard passes, and the defect surfaces on a page nobody reread. It is
// the most likely regression of a restructuring of `T`, and the only one of this
// PR that can be caught without a browser.

import assert from "node:assert/strict";
import test from "node:test";
import {
  CHOICE_LABELS,
  CHOICE_LABELS_SHORT,
  CONFIDENCE_LABELS,
  CORPUS_LANG,
  LANGS,
  T,
  THEMES,
  reading,
} from "./ui.js";

// Every table below is indexed by language code and must answer for all of them.
const TABLES = { T, THEMES, CONFIDENCE_LABELS, CHOICE_LABELS, CHOICE_LABELS_SHORT };

for (const [name, table] of Object.entries(TABLES)) {
  test(`${name} covers every language`, () => {
    assert.deepEqual(Object.keys(table).sort(), [...LANGS].sort());
  });

  test(`${name} holds the same keys in every language`, () => {
    const [reference, ...others] = LANGS;
    const expected = Object.keys(table[reference]).sort();
    for (const lang of others) {
      assert.deepEqual(
        Object.keys(table[lang]).sort(),
        expected,
        `${name}.${lang} and ${name}.${reference} do not hold the same keys`,
      );
    }
  });

  test(`${name} holds no empty value in any language`, () => {
    for (const lang of LANGS) {
      for (const [key, value] of Object.entries(table[lang])) {
        assert.ok(
          typeof value === "function" || (Array.isArray(value) ? value.length > 0 : value !== ""),
          `${name}.${lang}.${key} is empty`,
        );
      }
    }
  });
}

// The header is a function, so its five statements escape the check above. DP-27
// caps it at five statements of 120 characters, and PR-14 loads one of them with
// the register marking of the English interface (F8).
test("the questionnaire header stays within the cap in every language", () => {
  for (const lang of LANGS) {
    const statements = T[lang].header(30, 4);
    assert.ok(statements.length <= 5, `${lang}: ${statements.length} statements, 5 allowed`);
    for (const statement of statements) {
      assert.ok(
        statement.length <= 120,
        `${lang}: "${statement}" is ${statement.length} characters, 120 allowed`,
      );
    }
  }
});

// The instrument stays in the language of the corpus whatever the interface, and
// the translation is only ever an addition to it. A `reading()` returning the
// English text as `text` would be the substitution DP-18 exists to forbid.
test("reading() never puts the translation in place of the statement", () => {
  const text = { fr: "énoncé", en: "statement" };
  for (const lang of LANGS) {
    assert.equal(reading(text, lang).text, text[CORPUS_LANG]);
  }
  assert.equal(reading(text, CORPUS_LANG).translation, null);
  assert.equal(reading(text, "en").translation, text.en);
});
