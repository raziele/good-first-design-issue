/**
 * E2E test skeleton: Claim Issue flow.
 * Spec: specs/uxi/flows/claim-issue.flow.md
 * Spec: specs/behavior/claim.spec.md — RULE-CLM-001 through RULE-CLM-004
 *
 * Framework: Playwright
 *
 * NOTE: These are skeletons. Selectors must be filled in once the frontend
 * component structure is finalized.
 */

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

test.describe("Claim Issue flow — specs/uxi/flows/claim-issue.flow.md", () => {

  // -------------------------------------------------------------------------
  // Entry point
  // -------------------------------------------------------------------------

  test("Claim CTA button is visible on issue detail view", async ({ page }) => {
    // TODO: navigate to a seeded issue detail page
    // await page.goto(`${BASE_URL}/issues/fixture-issue-1`);
    // await expect(page.locator('[data-testid="claim-cta"]')).toBeVisible();
    test.fixme(true, "TODO: assert Claim This Task CTA is visible on detail view");
  });

  // -------------------------------------------------------------------------
  // Claim options modal — RULE-CLM-001
  // -------------------------------------------------------------------------

  test('clicking "Claim This Task" opens claim options modal', async ({ page }) => {
    // await page.goto(`${BASE_URL}/issues/fixture-issue-1`);
    // await page.locator('[data-testid="claim-cta"]').click();
    // await expect(page.locator('[data-testid="claim-modal"]')).toBeVisible();
    test.fixme(true, "TODO: assert modal opens on CTA click");
  });

  test('modal title reads "Ready to claim this task?"', async ({ page }) => {
    // await page.locator('[data-testid="claim-modal-title"]').toContainText(
    //   "Ready to claim this task?"
    // );
    test.fixme(true, "TODO: assert modal title copy");
  });

  test("modal shows AI-generated comment preview", async ({ page }) => {
    // await expect(page.locator('[data-testid="claim-comment-preview"]')).toBeVisible();
    test.fixme(true, "TODO: assert comment preview is rendered in modal");
  });

  test('modal shows "Go to GitHub" primary button and "Copy comment" secondary button', async ({ page }) => {
    // await expect(page.locator('[data-testid="claim-go-to-github"]')).toBeVisible();
    // await expect(page.locator('[data-testid="claim-copy-comment"]')).toBeVisible();
    test.fixme(true, "TODO: assert both action buttons are visible");
  });

  // -------------------------------------------------------------------------
  // Path A: Go to GitHub — RULE-CLM-001
  // -------------------------------------------------------------------------

  test('"Go to GitHub" opens GitHub issue in new tab', async ({ page, context }) => {
    // const [newPage] = await Promise.all([
    //   context.waitForEvent("page"),
    //   page.locator('[data-testid="claim-go-to-github"]').click(),
    // ]);
    // await expect(newPage).toHaveURL(/github\.com\/.+\/issues\/\d+/);
    test.fixme(true, "TODO: assert new tab opens to GitHub issue URL");
  });

  test("GitHub URL has pre-filled comment via body param or anchor", async ({ page }) => {
    // TODO: intercept new tab URL, assert it contains the comment param
    test.fixme(true, "TODO: assert GitHub URL contains pre-filled comment");
  });

  // -------------------------------------------------------------------------
  // Path B: Copy to clipboard — RULE-CLM-001
  // -------------------------------------------------------------------------

  test('"Copy comment" copies AI comment to clipboard', async ({ page, context }) => {
    // await context.grantPermissions(["clipboard-write", "clipboard-read"]);
    // await page.locator('[data-testid="claim-copy-comment"]').click();
    // const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    // expect(clipboardText.length).toBeGreaterThan(0);
    test.fixme(true, "TODO: assert clipboard content after copy action");
  });

  test('clipboard success toast reads "Comment copied!"', async ({ page }) => {
    // await expect(page.locator('[data-testid="toast"]')).toContainText("Comment copied!");
    test.fixme(true, "TODO: assert toast message matches voice-and-tone.md copy");
  });

  test("clipboard success toast auto-dismisses after 3 seconds", async ({ page }) => {
    // await page.locator('[data-testid="claim-copy-comment"]').click();
    // await page.waitForTimeout(3500);
    // await expect(page.locator('[data-testid="toast"]')).not.toBeVisible();
    test.fixme(true, "TODO: assert toast disappears after 3s");
  });

  // -------------------------------------------------------------------------
  // Already claimed state — RULE-CLM-004
  // -------------------------------------------------------------------------

  test("already-claimed issue shows 'Already claimed' badge on detail view", async ({ page }) => {
    // TODO: seed issue with is_claimed=true
    // await expect(page.locator('[data-testid="claimed-badge"]')).toContainText("Already claimed");
    test.fixme(true, "TODO: seed claimed issue and assert badge");
  });

  test("claim CTA is still enabled for already-claimed issue", async ({ page }) => {
    // Spec: no warning or block shown
    // await expect(page.locator('[data-testid="claim-cta"]')).not.toBeDisabled();
    test.fixme(true, "TODO: assert CTA is not disabled for is_claimed=true issue");
  });

  // -------------------------------------------------------------------------
  // Edge cases — claim-issue.flow.md
  // -------------------------------------------------------------------------

  test("clipboard API failure shows fallback manual selection message", async ({ page }) => {
    // TODO: mock clipboard to fail, assert error message
    // "Couldn't copy. Try selecting the text manually."
    test.fixme(true, "TODO: simulate clipboard failure and assert fallback message");
  });

  test("popup blocker shows fallback GitHub link", async ({ page }) => {
    // TODO: simulate popup blocker, assert fallback link appears
    // "Click here to open on GitHub"
    test.fixme(true, "TODO: simulate popup blocker and assert fallback link");
  });

  test("claim flow on mobile uses bottom sheet instead of modal", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 }); // iPhone 14
    // TODO: assert bottom sheet component renders instead of dialog
    test.fixme(true, "TODO: assert bottom sheet on mobile viewport");
  });
});
