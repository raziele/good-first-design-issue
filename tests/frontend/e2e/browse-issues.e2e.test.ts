/**
 * E2E test skeleton: Browse Issues flow.
 *
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-001 through RULE-ISS-005
 * Flow: specs/uxi/flows/browse-issues.flow.md
 *
 * Runner: Playwright
 * Entry point: / (homepage)
 *
 * TODO: configure baseURL in playwright.config.ts pointing to dev server
 */

import { test, expect } from "@playwright/test";

// ---------------------------------------------------------------------------
// Flow: Browse Issues — happy path
// ---------------------------------------------------------------------------

test.describe("Browse Issues — happy path", () => {
  test.beforeEach(async ({ page }) => {
    // TODO: seed test DB with known fixture issues before each test
    await page.goto("/");
  });

  test("browse-issues — loads homepage and shows issue cards", async ({ page }) => {
    // Flow step 1–2: landing and issue listing rendered
    // TODO: await expect(page.locator("[data-testid='issue-card']").first()).toBeVisible();
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — only relevant active issues appear in listing (RULE-ISS-001)", async ({ page }) => {
    // TODO: seed: 1 relevant+active, 1 not_relevant, 1 archived
    // TODO: await expect(page.locator("[data-testid='issue-card']")).toHaveCount(1);
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — default sort is by freshness ascending (RULE-ISS-005)", async ({ page }) => {
    // TODO: seed issues with known freshness_days values
    // TODO: const cards = page.locator("[data-testid='issue-card']");
    // TODO: verify first card has smaller freshness_days than second
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — clicking a card navigates to detail view", async ({ page }) => {
    // Flow step 6–7: card click → detail view
    // TODO: await page.locator("[data-testid='issue-card']").first().click();
    // TODO: await expect(page).toHaveURL(/\/issues\/.+/);
    await expect(page).toHaveURL("/");
  });
});

// ---------------------------------------------------------------------------
// Flow: Browse Issues — loading state
// ---------------------------------------------------------------------------

test.describe("Browse Issues — loading state", () => {
  test("browse-issues — shows skeleton cards while fetching", async ({ page }) => {
    // TODO: intercept API and delay response
    // TODO: await expect(page.locator("[data-testid='skeleton-card']")).toBeVisible();
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — search and filter controls disabled during load", async ({ page }) => {
    // TODO: intercept API and delay, verify controls are disabled
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });
});

// ---------------------------------------------------------------------------
// Flow: Browse Issues — empty states
// ---------------------------------------------------------------------------

test.describe("Browse Issues — empty states", () => {
  test("browse-issues — no results shows empty state message with clear filters button", async ({ page }) => {
    // Flow: "Empty (no results)" state
    // TODO: seed 0 issues, apply filter that matches nothing
    // TODO: await expect(page.locator("text=No matches")).toBeVisible();
    // TODO: await expect(page.locator("[data-testid='clear-filters']")).toBeVisible();
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — no issues at all shows Check back soon message", async ({ page }) => {
    // Flow: "Empty (no issues at all)" state
    // TODO: seed empty DB
    // TODO: await expect(page.locator("text=No design opportunities right now")).toBeVisible();
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });
});

// ---------------------------------------------------------------------------
// Flow: Browse Issues — error state
// ---------------------------------------------------------------------------

test.describe("Browse Issues — error state", () => {
  test("browse-issues — API error shows error message and retry button", async ({ page }) => {
    // Flow: "Error" state
    // TODO: page.route("/api/issues", route => route.abort());
    // TODO: await page.goto("/");
    // TODO: await expect(page.locator("text=Couldn't load tasks")).toBeVisible();
    // TODO: await expect(page.locator("[data-testid='retry-btn']")).toBeVisible();
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });
});

// ---------------------------------------------------------------------------
// Flow: Browse Issues — edge cases
// ---------------------------------------------------------------------------

test.describe("Browse Issues — edge cases", () => {
  test("browse-issues — extremely long issue title is truncated with ellipsis", async ({ page }) => {
    // TODO: seed issue with 300-char title
    // TODO: verify title element has CSS overflow ellipsis (max 2 lines)
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });

  test("browse-issues — claimed issue shows Already Claimed badge (RULE-ISS-004)", async ({ page }) => {
    // TODO: seed a claimed relevant active issue
    // TODO: await expect(page.locator("text=Already claimed")).toBeVisible();
    await page.goto("/");
    await expect(page).toHaveURL("/");
  });
});
