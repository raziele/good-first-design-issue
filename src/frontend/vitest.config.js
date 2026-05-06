import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

const workspaceRoot = path.resolve(__dirname, "../../");

export default defineConfig({
  plugins: [react()],
  root: workspaceRoot,
  test: {
    environment: "jsdom",
    globals: true,
    include: [
      "tests/frontend/component/**/*.test.ts",
      "tests/frontend/unit/**/*.test.ts",
    ],
  },
});
