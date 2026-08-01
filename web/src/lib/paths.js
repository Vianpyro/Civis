/**
 * Site root without a trailing slash: "" on a domain root, "/Civis" under a
 * GitHub Pages project path. Every internal link is built from this, so moving
 * the site is a one-line change in astro.config.mjs.
 */
export const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

export const href = (path) => `${BASE}/${path.replace(/^\//, "")}`;

/**
 * Counter service origin, or "" when there is none.
 *
 * Empty is a supported deployment, not a misconfiguration: the questionnaire,
 * the scoring and the reveal are entirely client-side. Without an API the site
 * loses aggregate statistics and nothing else — so when it is unset we hide the
 * opt-in rather than offering to send answers nowhere.
 */
export const API = (import.meta.env.PUBLIC_CIVIS_API ?? "").replace(/\/$/, "");

/**
 * Build provenance, injected by .github/workflows/pages.yml.
 *
 * Empty outside CI, and the footer then says the build is local. A made-up
 * commit id or date on the very component that carries provenance would
 * contradict what that component exists to state, so there is no fallback
 * value — only a named state.
 */
export const COMMIT = import.meta.env.PUBLIC_CIVIS_COMMIT ?? "";
export const BUILD_DATE = import.meta.env.PUBLIC_CIVIS_BUILD_DATE ?? "";

/** Run that fetched the sources and checked every quote word for word. */
export const CI_RUN_URL = import.meta.env.PUBLIC_CIVIS_RUN_URL ?? "";

export const REPO_URL = "https://github.com/Vianpyro/Civis";
