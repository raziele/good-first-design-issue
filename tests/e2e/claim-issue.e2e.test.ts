/**
 * E2E skeleton: Claim Issue flow.
 *
 * UXI Flow: specs/uxi/flows/claim-issue.flow.md
 * Behavior: specs/behavior/claim.spec.md (RULE-CLM-001 through RULE-CLM-004)
 * Glossary: TERM-002 (Claim), TERM-012 (Claim Comment)
 */

import { test, expect } from "@playwright/test";

test.describe("Claim Issue flow", () => {
  // Entry point: issue detail view
  test.beforeEach(async ({ page }) => {
    // TODO: Replace with a seeded issue ID once fixtures are in place.
    await page.goto("/issues/test-issue-001");
  });

  // ---------------------------------------------------------------------------
  // Step 1: Claim CTA visible
  // ---------------------------------------------------------------------------

  test("claim_issue_cta_is_visible_on_detail_page", async ({ page }) => {
    await expect(page.locator("text=Claim This Task")).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // Step 2: Claim modal / sheet appears (RULE-CLM-001)
  // ---------------------------------------------------------------------------

  test("claim_issue_modal_opens_with_two_options", async ({ page }) => {
    await page.locator("text=Claim This Task").click();
    await expect(page.locator("text=Ready to claim this task?")).toBeVisible();
    await expect(page.locator("text=Go to GitHub")).toBeVisible();
    await expect(page.locator("text=Copy comment")).toBeVisible();
  });

  test("claim_issue_modal_shows_ai_comment_preview", async ({ page }) => {
    await page.locator("text=Claim This Task").click();
    // The modal must display a comment preview (RULE-CLM-002)
    const preview = page.locator("[data-testid='claim-comment-preview']");
    await expect(preview).toBeVisible();
    const text = await preview.textContent();
    expect(text?.length).toBeGreaterThan(0);
  });

  test("claim_issue_modal_has_cancel_option", async ({ page }) => {
    await page.locator("text=Claim This Task").click();
    // Cancel must be reachable (close button or explicit cancel)
    const closeButton = page.locator("[data-testid='modal-close'], [aria-label='Close']");
    await expect(closeButton).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // Path A: Go to GitHub (RULE-CLM-001)
  // ---------------------------------------------------------------------------

  test("claim_issue_go_to_github_opens_new_tab_with_prefilled_comment", async ({ page, context }) => {
    // Capture the new tab that opens
    const [newPage] = await Promise.all([
      context.waitForEvent("page"),
      (async () => {
        await page.locator("text=Claim This Task").click();
        await page.locator("text=Go to GitHub").click();
      })(),
    ]);
    // Must navigate to GitHub
    await newPage.waitForLoadState();
    expect(newPage.url()).toContain("github.com");
    expect(newPage.url()).toContain("body=");
  });

  // ---------------------------------------------------------------------------
  // Path B: Copy comment (RULE-CLM-001)
  // ---------------------------------------------------------------------------

  test("claim_issue_copy_comment_shows_confirmation_toast", async ({ page }) => {
    await page.locator("text=Claim This Task").click();
    await page.locator("text=Copy comment").click();
    // Clipboard success toast (from voice-and-tone.md: "Comment copied!")
    await expect(page.locator("text=Comment copied!")).toBeVisible();
  });

  test("claim_issue_copy_comment_toast_auto_dismisses", async ({ page }) => {
    await page.locator("text=Claim This Task").click();
    await page.locator("text=Copy comment").click();
    const toast = page.locator("text=Comment copied!");
    await expect(toast).toBeVisible();
    // Auto-dismiss after 3 seconds
    await page.waitForTimeout(3500);
    await expect(toast).not.toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // RULE-CLM-003: No local claim tracking
  // ---------------------------------------------------------------------------

  test("claim_issue_does_not_immediately_change_is_claimed_status", async ({ page }) => {
    // After claiming, the page should NOT immediately flip to "Already claimed"
    // (that only happens after the next ETL refresh)
    const badgeBefore = page.locator("text=Already claimed");
    const wasClaimedBefore = await badgeBefore.isVisible();

    await page.locator("text=Claim This Task").click();
    await page.locator("text=Copy comment").click();

    // Reload page to simulate fresh state (without ETL)
    await page.reload();
    const badgeAfter = page.locator("text=Already claimed");
    const isClaimedAfter = await badgeAfter.isVisible();

    // Claim status should not have changed locally
    expect(isClaimedAfter).toBe(wasClaimedBefore);
  });

  // ---------------------------------------------------------------------------
  // RULE-CLM-004: Multiple users / already-claimed issues
  // ---------------------------------------------------------------------------

  test("claim_issue_already_claimed_badge_visible_but_cta_still_present", async ({ page }) => {
    // TODO: Navigate to a seeded issue with is_claimed=true
    // await page.goto("/issues/already-claimed-issue-id");
    // await expect(page.locator("text=Already claimed")).toBeVisible();
    // await expect(page.locator("text=Claim This Task")).toBeVisible();
    test.skip(true, "TODO: Seed a claimed issue fixture");
  });

  // ---------------------------------------------------------------------------
  // Edge cases (claim-issue.flow.md)
  // ---------------------------------------------------------------------------

  test("claim_issue_clipboard_failure_shows_manual_copy_hint", async ({ page }) => {
    // TODO: Override clipboard API to reject
    // await page.addInitScript(() => {
    //   navigator.clipboard.writeText = () => Promise.reject(new Error("denied"));
    // });
    // await page.locator("text=Claim This Task").click();
    // await page.locator("text=Copy comment").click();
    // await expect(page.locator("text=Couldn't copy")).toBeVisible();
    test.skip(true, "TODO: Override clipboard API in test context");
  });

  test("claim_issue_mobile_uses_bottom_sheet_instead_of_modal", async ({ page, browser }) => {
    // TODO: Use mobile viewport
    // const mobilePage = await browser.newPage({ viewport: { width: 390, height: 844 } });
    // await mobilePage.goto("/issues/test-issue-001");
    // await mobilePage.locator("text=Claim This Task").click();
    // await expect(mobilePage.locator("[data-testid='bottom-sheet']")).toBeVisible();
    test.skip(true, "TODO: Use mobile viewport fixture");
  });
});
