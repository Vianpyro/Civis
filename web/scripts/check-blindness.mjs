/**
 * Blindness guard (INV-01, DT-05).
 *
 * Fails if the compiled questionnaire page — or any JavaScript asset it
 * references — contains a formation id, name or acronym.
 *
 * Runs after `npm run build`, and deliberately not under `node --test`: the
 * test runner executes *before* the build in CI, so a check named like a test
 * would inspect a missing or stale dist and pass without looking at anything.
 * That is the worst failure mode available to a guard, hence the name.
 */
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { LANGS } from "../src/lib/ui.js";

const here = dirname(fileURLToPath(import.meta.url));
const DIST = resolve(here, "../dist");
const PROGRAMS = resolve(here, "../../content/programs");

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory() ? walk(join(dir, entry.name)) : [join(dir, entry.name)],
  );

const rel = (file) => file.slice(resolve(here, "..").length + 1).replaceAll("\\", "/");

const die = (message) => {
  console.error(`blindness check: ${message}`);
  process.exit(1);
};

/**
 * Terms are read from content/programs at run time, never copied here. A
 * hardcoded list would silently stop covering a formation the day one is added,
 * and the check would still report success.
 */
function forbiddenTerms() {
  if (!existsSync(PROGRAMS)) die(`no programs directory at ${PROGRAMS}`);
  const terms = new Map();
  for (const file of walk(PROGRAMS).filter((f) => f.endsWith(".json"))) {
    const { party, points = [] } = JSON.parse(readFileSync(file, "utf8"));
    const source = basename(file);
    for (const term of [party?.id, party?.name, party?.short, ...points.map((p) => p.id)]) {
      if (term) terms.set(term, source);
    }
  }
  if (terms.size === 0) die(`no formation term found under ${PROGRAMS}`);
  return terms;
}

/**
 * Built questionnaire pages: `<lang>/index.html` for every language of LANGS,
 * wherever the build put them. Looked up rather than hardcoded — `base` is
 * expected to change on a move to a custom domain, and a path frozen here would
 * turn this into a green check over zero files.
 */
function questionnairePages() {
  if (!existsSync(DIST)) die(`no build output at ${DIST} — run \`npm run build\` first`);
  const pages = walk(DIST).filter(
    (file) => basename(file) === "index.html" && LANGS.includes(basename(dirname(file))),
  );
  if (pages.length === 0) die(`no questionnaire page found under ${DIST}`);
  return pages;
}

/** JavaScript referenced by a page, resolved to a file inside dist. */
function referencedScripts(page, html) {
  const files = [];
  for (const [, url] of html.matchAll(/(?:src|href)="([^"]+\.m?js)(?:[?#][^"]*)?"/g)) {
    const file = url.startsWith("/") ? fromSiteRoot(url) : resolve(dirname(page), url);
    if (!file) die(`${rel(page)} references ${url}, which is not in the build output`);
    files.push(file);
  }
  return files;
}

/**
 * Site-absolute URLs carry the `base` prefix, which is not part of the dist
 * tree. Drop leading segments until the rest exists rather than assuming a
 * value for `base`.
 */
function fromSiteRoot(url) {
  const segments = url.split("/").filter(Boolean);
  for (let i = 0; i < segments.length; i += 1) {
    const candidate = resolve(DIST, segments.slice(i).join("/"));
    if (existsSync(candidate)) return candidate;
  }
  return null;
}

/**
 * Word boundaries are Unicode-aware: `\b` would not do, and a bare substring
 * search makes a two-letter acronym match inside "gove(rn)ment" or "bo(rn)".
 *
 * ponytail: case-insensitive, not accent-insensitive. Terms and build output
 * come from the same JSON, so a leak carries the accents it was written with.
 */
const matcher = (term) =>
  new RegExp(
    `(?<![\\p{L}\\p{N}])${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![\\p{L}\\p{N}])`,
    "giu",
  );

function position(text, index) {
  const before = text.slice(0, index);
  const line = before.split("\n").length;
  return `${line}:${index - before.lastIndexOf("\n")}`;
}

const terms = forbiddenTerms();
const pages = questionnairePages();
const checked = new Set();
const failures = [];

for (const page of pages) {
  const html = readFileSync(page, "utf8");
  for (const file of [page, ...referencedScripts(page, html)]) {
    if (checked.has(file)) continue;
    checked.add(file);
    const text = file === page ? html : readFileSync(file, "utf8");
    for (const [term, source] of terms) {
      for (const match of text.matchAll(matcher(term))) {
        failures.push(
          `${rel(file)}:${position(text, match.index)} — "${match[0]}" (${term}, from ${source})`,
        );
      }
    }
  }
}

if (failures.length > 0) {
  console.error(`blindness check: formation data reached the questionnaire bundle (INV-01)`);
  for (const failure of failures) console.error(`  ${failure}`);
  process.exit(1);
}

console.log(
  `blindness check: ${checked.size} file(s) clear of ${terms.size} formation term(s)`,
);
