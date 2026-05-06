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
    include: ["../../tests/frontend/component/**/*.test.ts", "../../tests/frontend/unit/**/*.test.ts"],
    environment: "node",
  },
});
