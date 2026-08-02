// Token test. Forbids hard-coded values outside tokens.css, so the interface
// system is a constraint rather than a convention (DT-04).
//
// Every exception below weakens this test. The list is meant to stay short and
// to be read as a signal in review: a list that grows from PR to PR is the
// symptom of a token scale that does not fit, and the scale is what gets revised
// — explicitly, in a PR of its own.

import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const SRC = dirname(fileURLToPath(import.meta.url));
const TOKEN_FILE = "tokens.css";

// The one file allowed to hold literal values. Everything else consumes it.
const files = (extension) => {
  const walk = (directory) =>
    readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
      const path = join(directory, entry.name);
      return entry.isDirectory() ? walk(path) : path.endsWith(extension) ? [path] : [];
    });
  return walk(SRC).map((path) => [relative(SRC, path).split("\\").join("/"), readFileSync(path, "utf8")]);
};

const stripComments = (source) => source.replace(/\/\*[\s\S]*?\*\//g, "");

const cssFiles = files(".css").map(([name, source]) => [name, stripComments(source)]);
const astroFiles = files(".astro");

const styleSheets = cssFiles.filter(([name]) => name !== TOKEN_FILE);

// --- Inline style attributes -------------------------------------------------
//
// No exception left. `inline-styles-questionnaire`, covering the 3 attributes of
// the questionnaire page, was retired by PR-04; `inline-styles-resultats`,
// covering the attributes of the results page, was retired by PR-10 when the
// client-rendered string templates that held them became markup. Every file is
// now held to zero.
//
// The map stays as the place a new exception would have to be declared, in the
// open, where a list that grows from PR to PR is visible in review (DT-04, G8).
const INLINE_STYLE_EXCEPTIONS = {};

// --- Value scales ------------------------------------------------------------

const COLOUR_LITERAL = /#[0-9a-f]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color-mix)\(/gi;

// Any tint property, however it is spelled. INV-12 is the point of this test.
const HUE_PROPERTY = /\b(?:accent-color|hue-rotate|filter\s*:\s*(?!none))/gi;

// Every absolute length carries a unit. `0` and layout percentages have none, so
// they fall outside this check by construction rather than by exception.
const LENGTH_LITERAL = /(?<![\w.-])\d*\.?\d+(px|rem|em|ch|ex|vh|vw|vmin|vmax|pt|pc|cm|mm|in|q)\b/gi;

const DURATION_LITERAL = /(?<![\w.-])(\d*\.?\d+)(ms|s)\b/gi;
const MAX_DURATION_MS = 120;

// --- Tests -------------------------------------------------------------------

test("tokens.css exists and is the only stylesheet holding literal values", () => {
  assert.ok(
    cssFiles.some(([name]) => name === TOKEN_FILE),
    "tokens.css must sit next to styles.css, not in a new directory",
  );
  assert.ok(styleSheets.length > 0, "expected at least one stylesheet consuming the tokens");
});

test("no colour literal outside tokens.css", () => {
  for (const [name, source] of [...styleSheets, ...astroFiles]) {
    const found = source.match(COLOUR_LITERAL) ?? [];
    assert.deepEqual(found, [], `${name} holds colour literals: ${found.join(", ")}`);
  }
});

test("no tint property is reintroduced", () => {
  for (const [name, source] of cssFiles) {
    const found = source.match(HUE_PROPERTY) ?? [];
    assert.deepEqual(found, [], `${name} reintroduces a tint property: ${found.join(", ")}`);
  }
});

test("no length or font-size literal outside tokens.css", () => {
  for (const [name, source] of styleSheets) {
    const found = source.match(LENGTH_LITERAL) ?? [];
    assert.deepEqual(found, [], `${name} holds length literals: ${found.join(", ")}`);
  }
});

test("no duration above the animation bound", () => {
  for (const [name, source] of cssFiles) {
    for (const [literal, amount, unit] of source.matchAll(DURATION_LITERAL)) {
      const ms = unit === "s" ? Number(amount) * 1000 : Number(amount);
      assert.ok(ms <= MAX_DURATION_MS, `${name} declares ${literal}, above ${MAX_DURATION_MS}ms`);
    }
  }
});

test("no inline style attribute outside the named exception", () => {
  for (const [name, source] of astroFiles) {
    const count = (source.match(/\sstyle\s*=\s*["'`]/g) ?? []).length;
    const exception = INLINE_STYLE_EXCEPTIONS[name];
    if (exception === undefined) {
      assert.equal(count, 0, `${name} holds ${count} inline style attribute(s)`);
      continue;
    }
    assert.equal(
      count,
      exception.count,
      `${name} holds ${count} inline style attribute(s); exception ${exception.name} covers ` +
        `${exception.count} and is retired by ${exception.retiredBy}`,
    );
  }
});

test("every declared inline-style exception still covers a file that exists", () => {
  for (const [path, exception] of Object.entries(INLINE_STYLE_EXCEPTIONS)) {
    assert.ok(
      astroFiles.some(([name]) => name === path),
      `exception ${exception.name} points at ${path}, which no longer exists`,
    );
  }
});
