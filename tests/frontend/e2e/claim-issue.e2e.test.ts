/**
 * E2E test skeleton: Claim Issue flow.
 *
 * Spec: specs/behavior/claim.spec.md — RULE-CLM-001 through RULE-CLM-004
 * Flow: specs/uxi/flows/claim-issue.flow.md
 *
 * Runner: Playwright
 * Entry point: Issue detail view (e.g. /issues/:id)
 *
 * TODO: configure baseURL in playwright.config.ts
 * TODO: seed DB with a known test issue before each test
 */

import { test, expect } from "@playwright/test";

const DETAIL_URL = "/issues/test-issue-001";

// ---------------------------------------------------------------------------
// Flow: Claim Issue — happy path A (Go to GitHub)
// ---------------------------------------------------------------------------

test.describe("Claim Issue — Path A: Go to GitHub", () => {
  test.beforeEach(async ({ page }) => {
    // TODO: seed active relevant issue with id=test-issue-001
    await page.goto(DETAIL_URL);
  });

  test("claim-issue — clicking Claim This Task opens claim options modal (RULE-CLM-001)", async ({ page }) => {
    // Flow step 1–2
    // TODO: await page.click("[data-testid='claim-cta']");
    // TODO: await expect(page.locator("text=Ready to claim this task?")).toBeVisible();
    await expect(page).toHaveURL(DETAIL_URL);
  });

  test("claim-issue — Go to GitHub option opens GitHub in new tab with prefilled comment (RULE-CLM-001)", async ({ page, context }) => {
    // Flow steps 3 → 4a → 5a
    // TODO: const [newPage] = await Promise.all([
    //   context.waitForEvent("page"),
    //   page.click("[data-testid='go-to-github-btn']"),
    // ]);
    // TODO: await newPage.waitForLoadState();
    // TODO: expect(newPage.url()).toContain("github.com");
    // TODO: expect(newPage.url()).toContain("new_comment_field");
    await expect(page).toHaveURL(DETAIL_URL);
  });
});

// ---------------------------------------------------------------------------
// Flow: Claim Issue — happy path B (Copy comment)
// ---------------------------------------------------------------------------

test.describe("Claim Issue — Path B: Copy Comment", () => {
  test.beforeEach(async ({ page }) => {
    // TODO: seed issue + grant clipboard-write permission
    await page.goto(DETAIL_URL);
  });

  test("claim-issue — Copy comment writes to clipboard and shows confirmation toast (RULE-CLM-001)", async ({ page }) => {
    // Flow steps 3 → 4b → 5b
    // TODO: await page.click("[data-testid='claim-cta']");
    // TODO: await page.click("[data-testid='copy-comment-btn']");
    // TODO: await expect(page.locator("text=Comment copied")).toBeVisible();
    // TODO: verify clipboard content matches AI-generated comment (needs clipboard read permission)
    await expect(page).toHaveURL(DETAIL_URL);
  });

  test("claim-issue — confirmation toast auto-dismisses after 3 seconds", async ({ page }) => {
    // Flow: Clipboard Confirmation state — auto-dismiss
    // TODO: click copy, wait 3s, verify toast gone
    // TODO: await page.waitForTimeout(3200);
    // TODO: await expect(page.locator("text=Comment copied")).not.toBeVisible();
    await expect(page).toHaveURL(DETAIL_URL);
  });
});

// ---------------------------------------------------------------------------
// Flow: Claim Issue — AI-generated comment (RULE-CLM-002)
// ---------------------------------------------------------------------------

test.describe("Claim Issue — AI claim comment content", () => {
  test("claim-issue — claim modal shows non-empty AI-generated comment preview (RULE-CLM-002)", async ({ page }) => {
    // TODO: await page.goto(DETAIL_URL);
    // TODO: await page.click("[data-testid='claim-cta']");
    // TODO: const preview = page.locator("[data-testid='claim-comment-preview']");
    // TODO: await expect(preview).toBeVisible();
    // TODO: const text = await preview.innerText();
    // TODO: expect(text.trim().length).toBeGreaterThan(0);
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });
});

// ---------------------------------------------------------------------------
// Flow: Claim Issue — no local tracking (RULE-CLM-003)
// ---------------------------------------------------------------------------

test.describe("Claim Issue — no local claim tracking", () => {
  test("claim-issue — claim action does not update is_claimed immediately in UI (RULE-CLM-003)", async ({ page }) => {
    // After claiming, the badge should NOT immediately appear — it reflects ETL state
    // TODO: await page.goto(DETAIL_URL);
    // TODO: perform claim action
    // TODO: await expect(page.locator("text=Already claimed")).not.toBeVisible();
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });
});

// ---------------------------------------------------------------------------
// Flow: Claim Issue — multiple claimants (RULE-CLM-004)
// ---------------------------------------------------------------------------

test.describe("Claim Issue — multiple claimants allowed", () => {
  test("claim-issue — already-claimed issue still shows claim CTA without blocking message (RULE-CLM-004)", async ({ page }) => {
    // TODO: seed issue with is_claimed=true
    // TODO: await page.goto(DETAIL_URL);
    // TODO: await expect(page.locator("[data-testid='claim-cta']")).toBeVisible();
    // TODO: await expect(page.locator("text=Cannot claim")).not.toBeVisible();
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });

  test("claim-issue — already-claimed issue shows Already Claimed badge alongside CTA", async ({ page }) => {
    // TODO: seed is_claimed=true issue
    // TODO: await expect(page.locator("text=Already claimed")).toBeVisible();
    // TODO: await expect(page.locator("[data-testid='claim-cta']")).toBeVisible();
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });
});

// ---------------------------------------------------------------------------
// Flow: Claim Issue — edge cases
// ---------------------------------------------------------------------------

test.describe("Claim Issue — edge cases", () => {
  test("claim-issue — popup blocker shows fallback link to GitHub", async ({ page }) => {
    // TODO: block popups, attempt Go to GitHub, verify fallback link visible
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });

  test("claim-issue — mobile uses bottom sheet instead of modal", async ({ page }) => {
    // TODO: page.setViewportSize({ width: 375, height: 812 });
    // TODO: verify bottom sheet rendered instead of centered modal
    await page.goto(DETAIL_URL);
    await expect(page).toHaveURL(DETAIL_URL);
  });
});
