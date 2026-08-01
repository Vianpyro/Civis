import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  vite: {
    // content/ is the source of truth and lives above web/. Importing it
    // directly keeps one copy; a build step that mirrored it into web/ would
    // just be a copy that can go stale.
    server: { fs: { allow: [".."] } },
  },
});
