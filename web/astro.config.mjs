import { defineConfig } from "astro/config";

// GitHub Pages serves this project at /Civis/. On a custom domain set BASE to ""
// and `site` to the domain — every internal link is derived from BASE_URL, so
// nothing else changes.
const BASE = "/Civis";

export default defineConfig({
  output: "static",
  site: "https://vianpyro.github.io",
  base: BASE,

  // `redirects` targets are written verbatim into the generated page: unlike
  // links built from BASE_URL, Astro does not prepend `base` here.
  redirects: { "/": `${BASE}/fr/` },

  vite: {
    // content/ is the source of truth and lives above web/. Importing it
    // directly keeps one copy; a build step that mirrored it into web/ would
    // just be a copy that can go stale.
    server: { fs: { allow: [".."] } },
  },
});
