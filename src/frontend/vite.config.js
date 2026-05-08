/// <reference types="vitest" />
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
    include: [
      "../../tests/frontend/**/*.{test,spec}.?(c|m)[jt]s?(x)",
    ],
    environment: "jsdom",
    globals: false,
  },
});
