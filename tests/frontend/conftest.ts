/**
 * Frontend test setup — runs before each test file.
 * Configures @testing-library/react cleanup.
 */
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
});
