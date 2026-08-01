// Contrast test. Reads the colour tokens and computes WCAG ratios from them, in
// both themes. Distinct from the token test on purpose (DT-04): the token test
// catches a value in the wrong format, this one catches a value in the right
// format at the wrong level — exactly the defect it was written against, where
// --line respected the token system while sitting at 1.37:1.
//
// If a pair fails, the token value changes. The threshold never does.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const css = readFileSync(new URL("./tokens.css", import.meta.url), "utf8").replace(
  /\/\*[\s\S]*?\*\//g,
  "",
);

// Exactly two declaration blocks: the light theme, then the dark override.
const blocks = [...css.matchAll(/:root\s*\{([^}]*)\}/g)].map(([, body]) => body);

const declarations = (body) =>
  Object.fromEntries(
    [...body.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)].map(([, name, value]) => [name, value.trim()]),
  );

const light = declarations(blocks[1] === undefined ? "" : blocks[0]);
const dark = { ...light, ...declarations(blocks[1] ?? "") };

const luminance = (hex) => {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const channel = parseInt(hex.slice(i, i + 2), 16) / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

const ratio = (a, b) => {
  const [high, low] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (high + 0.05) / (low + 0.05);
};

const COLOUR_TOKENS = ["--paper", "--ink", "--ink-quiet", "--rule", "--edge", "--paper-inverse"];

// Every constrained pair, with the threshold it must clear.
const PAIRS = [
  { fg: "--ink", bg: "--paper", min: 7 },
  { fg: "--ink-quiet", bg: "--paper", min: 7 },
  { fg: "--edge", bg: "--paper", min: 3 },
  { fg: "--paper-inverse", bg: "--ink", min: 7 },
];

const THEMES = [
  ["light", light],
  ["dark", dark],
];

test("tokens.css declares one :root per theme", () => {
  assert.equal(blocks.length, 2, "expected :root and a single prefers-color-scheme override");
});

test("every colour token is a literal 6-digit hex in both themes", () => {
  for (const [name, tokens] of THEMES) {
    for (const token of COLOUR_TOKENS) {
      assert.match(
        tokens[token] ?? "",
        /^#[0-9a-f]{6}$/i,
        `${token} in the ${name} theme must be a 6-digit hex so it can be measured`,
      );
    }
  }
});

for (const [name, tokens] of THEMES) {
  for (const { fg, bg, min } of PAIRS) {
    test(`${fg} on ${bg} clears ${min}:1 in the ${name} theme`, () => {
      const measured = ratio(tokens[fg], tokens[bg]);
      console.log(
        `${name.padEnd(5)} ${fg} on ${bg}: ${measured.toFixed(2)}:1 (min ${min}:1)`,
      );
      assert.ok(
        measured >= min,
        `${fg} on ${bg} measures ${measured.toFixed(2)}:1 in the ${name} theme, below ${min}:1`,
      );
    });
  }
}
