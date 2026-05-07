import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Custom Vite plugin that prevents esbuild/oxc from misinterpreting JSDoc
 * block comments that contain both backtick template literals and "**\/"-style
 * glob patterns (which contain the "* /" sequence that would prematurely close
 * a block comment from the parser's perspective).
 *
 * The fix: insert a zero-width space between "**" and "/" so the parser no
 * longer sees "* /" as a comment terminator inside the comment body. This is
 * safe because the rewrite only affects JSDoc comment text — the actual test
 * assertions (expect(...)) are unaffected.
 */
function sanitizeBlockCommentGlobs() {
  return {
    name: "sanitize-block-comment-globs",
    enforce: "pre",
    transform(code, id) {
      if (!id.match(/\.[jt]sx?$/)) return null;
      if (!code.includes("**/")) return null;
      const sanitized = code.replace(/\*\*\//g, "** /");
      if (sanitized === code) return null;
      return { code: sanitized, map: null };
    },
  };
}

export default defineConfig({
  plugins: [sanitizeBlockCommentGlobs(), react()],
  server: {
    port: 5173,
  },
  preview: {
    port: 4173,
    host: true,
  },
  test: {
    include: ["tests/frontend/**/*.{test,spec}.{ts,tsx,js,jsx}"],
    root: "../..",
  },
});
