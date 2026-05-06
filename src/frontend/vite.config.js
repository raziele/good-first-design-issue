import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  preview: {
    port: 4173,
    host: true,
  },
  test: {
    environment: "jsdom",
    include: ["../../tests/frontend/**/*.test.ts", "../../tests/frontend/**/*.test.tsx"],
    globals: true,
  },
  server: {
    fs: {
      allow: ["/home/runner/work/good-first-design-issue/good-first-design-issue"],
    },
  },
});
