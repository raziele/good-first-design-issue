/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    fs: {
      allow: ["../.."],
    },
  },
  preview: {
    port: 4173,
    host: true,
  },
  resolve: {
    alias: {
      "../../src/frontend/src": path.resolve(__dirname, "src"),
    },
  },
  test: {
    include: [
      "../../tests/frontend/**/*.{test,spec}.?(c|m)[jt]s?(x)",
    ],
    environment: "jsdom",
    globals: false,
    server: {
      fs: {
        allow: [path.resolve(__dirname, "../..")],
      },
    },
  },
});
