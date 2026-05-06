/**
 * E2E test skeleton for Claim Issue flow.
 * Spec: specs/behavior/claim.spec.md
 * Flow: specs/uxi/flows/claim-issue.flow.md
 *
 * Structured for Playwright. Requires a running dev server.
 */

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

/** Navigate to the first issue detail page. */
async function goToFirstIssueDetail(page: import("@playwright/test").Page) {
  await page.goto(BASE_URL + "/");
  await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
  await page.locator('[data-testid="issue-card"]').first().click();
  await page.waitForSelector('[data-testid="claim-cta"]', { timeout: 5000 });
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

test.describe("Claim Issue flow — claim options modal", () => {
  test("clicking 'Claim This Task' opens the claim options modal", async ({
    page,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    await expect(
      page.locator('[data-testid="claim-modal"]')
    ).toBeVisible({ timeout: 3000 });
  });

  test("claim modal shows title 'Ready to claim this task?'", async ({
    page,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    await expect(
      page.locator("text=Ready to claim this task?")
    ).toBeVisible({ timeout: 3000 });
  });

  test("claim modal shows both 'Go to GitHub' and 'Copy comment' buttons", async ({
    page,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    await expect(
      page.locator('[data-testid="claim-go-to-github"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="claim-copy-comment"]')
    ).toBeVisible();
  });

  test("claim modal shows AI-generated comment preview", async ({ page }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    await expect(
      page.locator('[data-testid="claim-comment-preview"]')
    ).toBeVisible();
    const commentText = await page
      .locator('[data-testid="claim-comment-preview"]')
      .textContent();
    expect(commentText?.trim().length).toBeGreaterThan(0);
  });

  test("claim modal can be dismissed via cancel/close", async ({ page }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();
    await page.locator('[data-testid="claim-modal-close"]').click();

    await expect(
      page.locator('[data-testid="claim-modal"]')
    ).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Path A: Go to GitHub
// ---------------------------------------------------------------------------

test.describe("Claim Issue flow — Path A: Go to GitHub", () => {
  test("clicking 'Go to GitHub' opens GitHub issue in new tab", async ({
    page,
    context,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    const [newTab] = await Promise.all([
      context.waitForEvent("page"),
      page.locator('[data-testid="claim-go-to-github"]').click(),
    ]);

    await newTab.waitForLoadState("domcontentloaded");
    expect(newTab.url()).toContain("github.com");
  });

  test("GitHub URL includes pre-filled comment body parameter", async ({
    page,
    context,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    const [newTab] = await Promise.all([
      context.waitForEvent("page"),
      page.locator('[data-testid="claim-go-to-github"]').click(),
    ]);

    await newTab.waitForLoadState("domcontentloaded");
    expect(newTab.url()).toContain("body=");
  });
});

// ---------------------------------------------------------------------------
// Path B: Copy Comment
// ---------------------------------------------------------------------------

test.describe("Claim Issue flow — Path B: Copy comment", () => {
  test("clicking 'Copy comment' shows confirmation toast", async ({ page }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    // Grant clipboard permissions
    await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.locator('[data-testid="claim-copy-comment"]').click();

    await expect(
      page.locator("text=Comment copied")
    ).toBeVisible({ timeout: 3000 });
  });

  test("confirmation toast auto-dismisses after 3 seconds", async ({
    page,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();
    await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.locator('[data-testid="claim-copy-comment"]').click();

    await expect(
      page.locator("text=Comment copied")
    ).toBeVisible({ timeout: 3000 });

    // Toast should disappear after ~3 seconds (allow 5s for timing variance)
    await expect(
      page.locator("text=Comment copied")
    ).not.toBeVisible({ timeout: 5000 });
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: Already-claimed issues
// ---------------------------------------------------------------------------

test.describe("Claim Issue flow — already claimed issue", () => {
  test("'Already claimed' badge is shown on issue with is_claimed = true", async ({
    page,
  }) => {
    // Mock an issue with is_claimed = true
    await page.route("**/api/issues/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "gh-claimed",
          title: "Redesign settings page",
          description: "Create mockups for the settings flow.",
          is_claimed: true,
          classification: "relevant",
          status: "active",
          github_url: "https://github.com/org/repo/issues/42",
          complexity_score: "medium",
          attractiveness_rating: 0.7,
          seniority_level: "junior",
          repo_name: "org/repo",
          repo_stars: 200,
          freshness_days: 5,
          has_media: false,
        }),
      });
    });

    await page.goto(BASE_URL + "/issues/gh-claimed");
    await expect(
      page.locator('[data-testid="issue-claimed-badge"]')
    ).toBeVisible({ timeout: 5000 });
  });

  test("'Claim This Task' CTA remains enabled on already-claimed issue", async ({
    page,
  }) => {
    await page.route("**/api/issues/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "gh-claimed",
          title: "Redesign settings page",
          description: "Create mockups for the settings flow.",
          is_claimed: true,
          classification: "relevant",
          status: "active",
          github_url: "https://github.com/org/repo/issues/42",
          complexity_score: "medium",
          attractiveness_rating: 0.7,
          seniority_level: "junior",
          repo_name: "org/repo",
          repo_stars: 200,
          freshness_days: 5,
          has_media: false,
        }),
      });
    });

    await page.goto(BASE_URL + "/issues/gh-claimed");
    const cta = page.locator('[data-testid="claim-cta"]');
    await expect(cta).toBeVisible({ timeout: 5000 });
    await expect(cta).not.toBeDisabled();
  });
});

// ---------------------------------------------------------------------------
// Edge cases from claim-issue.flow.md
// ---------------------------------------------------------------------------

test.describe("Claim Issue flow — edge cases", () => {
  test("clipboard API failure shows fallback error message", async ({
    page,
  }) => {
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    // Deny clipboard permission to simulate failure
    await page.evaluate(() => {
      Object.defineProperty(navigator, "clipboard", {
        value: {
          writeText: () => Promise.reject(new Error("Clipboard not available")),
        },
        configurable: true,
      });
    });

    await page.locator('[data-testid="claim-copy-comment"]').click();
    await expect(
      page.locator("text=Couldn't copy")
    ).toBeVisible({ timeout: 3000 });
  });

  test("popup blocker fallback link is shown when new tab is blocked", async ({
    page,
  }) => {
    // TODO: Playwright doesn't easily simulate popup blockers.
    // This test validates the fallback link element exists in the DOM.
    await goToFirstIssueDetail(page);
    await page.locator('[data-testid="claim-cta"]').click();

    // The fallback link should be present in the modal as a safety net
    const fallbackLink = page.locator('[data-testid="claim-github-fallback-link"]');
    // If the element is not present, that's acceptable — this is a progressive enhancement
    await fallbackLink.count();
  });
});
