import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite plugin that sanitizes TypeScript files before esbuild sees them.
 * Handles "*\/" sequences that prematurely terminate JSDoc block comments.
 */
function sanitizeJsDocPlugin() {
  return {
    name: "sanitize-jsdoc",
    enforce: "pre",
    transform(code, id) {
      if (!id.endsWith(".ts") && !id.endsWith(".tsx")) return null;
      // In JSDoc block comments, a string literal like "**/foo" contains "*/"
      // which prematurely terminates the outer comment block for esbuild.
      // Replace any `"***/...` patterns (quote followed by stars then slash)
      // with a space inserted before the slash, making it harmless.
      let result = code.replace(/"(\*+)\//g, '"$1 /');

      if (result !== code) {
        return { code: result, map: null };
      }
      return null;
    },
  };
}

export default defineConfig({
  plugins: [sanitizeJsDocPlugin(), react()],
  server: {
    port: 5173,
  },
  preview: {
    port: 4173,
    host: true,
  },
  test: {
    include: ["../../tests/frontend/**/*.{test,spec}.{js,ts,jsx,tsx}"],
    environment: "node",
  },
});
