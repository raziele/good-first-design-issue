/**
 * E2E test skeleton for Claim Issue flow.
 * Spec: specs/behavior/claim.spec.md
 * Flow: specs/uxi/flows/claim-issue.flow.md
 *
 * Uses Playwright. Clipboard and window.open are mocked for hermeticity.
 */

import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_ISSUE = {
  id: "issue-001",
  repo_name: "owner/design-system",
  repo_stars: 1200,
  title: "Create wireframes for settings page",
  description: "We need mockup, user flow, and Figma designs for the new settings page.",
  description_truncated: "We need mockup, user flow, and Figma designs.",
  complexity_score: "medium",
  attractiveness_rating: 0.8,
  seniority_level: "junior",
  freshness_days: 3,
  has_media: false,
  is_claimed: false,
  classification: "relevant",
  status: "active",
  github_url: "https://github.com/owner/design-system/issues/1",
  claim_comment:
    "Hey! I'd love to take this on. I'm a designer looking to contribute — expect an update soon.",
};

async function setupDetailPage(page: Page, issue = MOCK_ISSUE) {
  await page.route(`**/api/issues/${issue.id}`, (route) =>
    route.fulfill({ json: issue })
  );
  await page.goto(`/issues/${issue.id}`);
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

test("claim-issue: clicking Claim This Task opens options modal", async ({ page }) => {
  await setupDetailPage(page);

  await page.getByTestId("claim-cta").click();
  await expect(page.getByTestId("claim-modal")).toBeVisible();
  await expect(page.getByTestId("claim-modal-title")).toContainText(
    "Ready to claim this task?"
  );
});

test("claim-issue: modal shows both Go to GitHub and Copy comment options", async ({ page }) => {
  await setupDetailPage(page);

  await page.getByTestId("claim-cta").click();
  await expect(page.getByTestId("claim-go-to-github")).toBeVisible();
  await expect(page.getByTestId("claim-copy-comment")).toBeVisible();
});

test("claim-issue: Go to GitHub opens GitHub with pre-filled comment", async ({ page, context }) => {
  await setupDetailPage(page);

  const [newPage] = await Promise.all([
    context.waitForEvent("page"),
    (async () => {
      await page.getByTestId("claim-cta").click();
      await page.getByTestId("claim-go-to-github").click();
    })(),
  ]);

  await newPage.waitForLoadState("domcontentloaded");
  expect(newPage.url()).toContain("github.com/owner/design-system/issues/1");
  expect(newPage.url()).toContain("body=");
});

test("claim-issue: Copy comment writes claim comment to clipboard", async ({ page }) => {
  await setupDetailPage(page);

  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);

  await page.getByTestId("claim-cta").click();
  await page.getByTestId("claim-copy-comment").click();

  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toContain("designer");
});

test("claim-issue: Copy comment shows confirmation toast", async ({ page }) => {
  await setupDetailPage(page);
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);

  await page.getByTestId("claim-cta").click();
  await page.getByTestId("claim-copy-comment").click();

  await expect(page.getByTestId("toast-confirmation")).toContainText("Comment copied");
});

// ---------------------------------------------------------------------------
// RULE-CLM-003: No local claim tracking
// ---------------------------------------------------------------------------

test("claim-issue: claim action does not POST to local /claims endpoint", async ({ page }) => {
  const localClaimRequests: string[] = [];
  page.on("request", (req) => {
    if (req.url().includes("/claims") && req.method() === "POST") {
      localClaimRequests.push(req.url());
    }
  });

  await setupDetailPage(page);
  await page.getByTestId("claim-cta").click();
  await page.getByTestId("claim-copy-comment").click();

  expect(localClaimRequests).toHaveLength(0);
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: Multiple users can claim same issue
// ---------------------------------------------------------------------------

test("claim-issue: already-claimed issue shows badge but CTA is not blocked", async ({ page }) => {
  const claimedIssue = { ...MOCK_ISSUE, is_claimed: true };
  await setupDetailPage(page, claimedIssue);

  await expect(page.getByTestId("claimed-badge")).toContainText("Already claimed");
  await expect(page.getByTestId("claim-cta")).toBeEnabled();
});

// ---------------------------------------------------------------------------
// Flow edge cases — claim-issue.flow.md
// ---------------------------------------------------------------------------

test("claim-issue: clipboard failure shows fallback error message", async ({ page }) => {
  await setupDetailPage(page);

  // Simulate clipboard API failure
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: () => Promise.reject(new Error("NotAllowedError")),
      },
      configurable: true,
    });
  });

  await page.goto(`/issues/${MOCK_ISSUE.id}`);
  await page.getByTestId("claim-cta").click();
  await page.getByTestId("claim-copy-comment").click();

  await expect(page.getByTestId("clipboard-error")).toContainText(
    "Couldn't copy. Try selecting the text manually."
  );
});

test("claim-issue: toast auto-dismisses after 3 seconds", async ({ page }) => {
  await setupDetailPage(page);
  await page.context().grantPermissions(["clipboard-read", "clipboard-write"]);

  await page.getByTestId("claim-cta").click();
  await page.getByTestId("claim-copy-comment").click();

  await expect(page.getByTestId("toast-confirmation")).toBeVisible();
  await page.waitForTimeout(3200);
  await expect(page.getByTestId("toast-confirmation")).not.toBeVisible();
});

test("claim-issue: modal has a close/cancel option", async ({ page }) => {
  await setupDetailPage(page);

  await page.getByTestId("claim-cta").click();
  await expect(page.getByTestId("claim-modal-close")).toBeVisible();
  await page.getByTestId("claim-modal-close").click();
  await expect(page.getByTestId("claim-modal")).not.toBeVisible();
});
