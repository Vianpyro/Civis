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
