/**
 * E2E test skeleton for Browse Issues flow.
 * Spec: specs/behavior/issues.spec.md
 * Flow: specs/uxi/flows/browse-issues.flow.md
 *
 * Uses Playwright. All network calls are intercepted via route mocking
 * to keep tests hermetic.
 */

import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_ISSUES = [
  {
    id: "issue-001",
    repo_name: "owner/design-system",
    repo_stars: 1200,
    title: "Create wireframes for settings page",
    description_truncated: "We need mockup and Figma designs for the settings page.",
    complexity_score: "medium",
    attractiveness_rating: 0.8,
    seniority_level: "junior",
    freshness_days: 3,
    has_media: false,
    is_claimed: false,
    classification: "relevant",
    status: "active",
    github_url: "https://github.com/owner/design-system/issues/1",
  },
  {
    id: "issue-002",
    repo_name: "owner/mobile-app",
    repo_stars: 400,
    title: "Redesign onboarding flow",
    description_truncated: "The current onboarding is confusing. We need a new user flow.",
    complexity_score: "high",
    attractiveness_rating: 0.9,
    seniority_level: "senior",
    freshness_days: 10,
    has_media: true,
    is_claimed: true,
    classification: "relevant",
    status: "active",
    github_url: "https://github.com/owner/mobile-app/issues/2",
  },
];

async function mockIssuesApi(page: Page, issues = MOCK_ISSUES) {
  await page.route("**/api/issues**", (route) =>
    route.fulfill({ json: { issues, total: issues.length } })
  );
}

// ---------------------------------------------------------------------------
// RULE-ISS-001 + RULE-ISS-002: Main listing shows relevant active issues
// ---------------------------------------------------------------------------

test("browse-issues: listing shows relevant active issue cards", async ({ page }) => {
  await mockIssuesApi(page);
  await page.goto("/");

  await expect(page.getByTestId("issue-card-issue-001")).toBeVisible();
});

test("browse-issues: issue card shows repo name, title, and scores", async ({ page }) => {
  await mockIssuesApi(page);
  await page.goto("/");

  const card = page.getByTestId("issue-card-issue-001");
  await expect(card.getByTestId("repo-name")).toContainText("owner/design-system");
  await expect(card.getByTestId("issue-title")).toContainText("Create wireframes");
  await expect(card.getByTestId("complexity-score")).toBeVisible();
  await expect(card.getByTestId("seniority-level")).toBeVisible();
  await expect(card.getByTestId("freshness-indicator")).toBeVisible();
});

test("browse-issues: media indicator shown when has_media is true", async ({ page }) => {
  await mockIssuesApi(page);
  await page.goto("/");

  const card = page.getByTestId("issue-card-issue-002");
  await expect(card.getByTestId("media-indicator")).toBeVisible();
});

test("browse-issues: no media indicator when has_media is false", async ({ page }) => {
  await mockIssuesApi(page);
  await page.goto("/");

  const card = page.getByTestId("issue-card-issue-001");
  await expect(card.getByTestId("media-indicator")).not.toBeVisible();
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues show badge
// ---------------------------------------------------------------------------

test("browse-issues: claimed issue shows 'Already claimed' badge", async ({ page }) => {
  await mockIssuesApi(page);
  await page.goto("/");

  const card = page.getByTestId("issue-card-issue-002");
  await expect(card.getByTestId("claimed-badge")).toContainText("Already claimed");
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort is by freshness
// ---------------------------------------------------------------------------

test("browse-issues: issues sorted by freshness (newest first) by default", async ({ page }) => {
  const issues = [
    { ...MOCK_ISSUES[0], id: "fresh", freshness_days: 2 },
    { ...MOCK_ISSUES[1], id: "old",   freshness_days: 20, is_claimed: false },
  ];
  await mockIssuesApi(page, issues);
  await page.goto("/");

  const cards = page.getByTestId(/^issue-card-/);
  const firstCard = cards.first();
  await expect(firstCard).toHaveAttribute("data-testid", "issue-card-fresh");
});

// ---------------------------------------------------------------------------
// RULE-ISS-003: Detail view
// ---------------------------------------------------------------------------

test("browse-issues: clicking a card navigates to detail view", async ({ page }) => {
  await mockIssuesApi(page);
  await page.route("**/api/issues/issue-001", (route) =>
    route.fulfill({ json: MOCK_ISSUES[0] })
  );
  await page.goto("/");

  await page.getByTestId("issue-card-issue-001").click();
  await expect(page).toHaveURL(/\/issues\/issue-001/);
});

test("browse-issues: detail view shows full description and github link", async ({ page }) => {
  const fullIssue = {
    ...MOCK_ISSUES[0],
    description: "Full description: We need mockup, user flow, and Figma designs for the new settings page.",
  };
  await page.route("**/api/issues/issue-001", (route) =>
    route.fulfill({ json: fullIssue })
  );
  await page.goto("/issues/issue-001");

  await expect(page.getByTestId("issue-description")).toContainText("Full description:");
  await expect(page.getByTestId("github-link")).toHaveAttribute(
    "href",
    "https://github.com/owner/design-system/issues/1"
  );
});

// ---------------------------------------------------------------------------
// Flow states
// ---------------------------------------------------------------------------

test("browse-issues: loading state shows skeleton cards", async ({ page }) => {
  // Delay response to observe loading state
  await page.route("**/api/issues**", async (route) => {
    await new Promise((r) => setTimeout(r, 500));
    await route.fulfill({ json: { issues: MOCK_ISSUES, total: 2 } });
  });
  await page.goto("/");
  await expect(page.getByTestId("skeleton-card")).toBeVisible();
});

test("browse-issues: empty state shown when no issues match", async ({ page }) => {
  await mockIssuesApi(page, []);
  await page.goto("/");
  await expect(page.getByTestId("empty-state")).toContainText("No design opportunities");
});

test("browse-issues: error state shows retry button", async ({ page }) => {
  await page.route("**/api/issues**", (route) => route.abort("failed"));
  await page.goto("/");
  await expect(page.getByTestId("error-state")).toContainText("Couldn't load tasks");
  await expect(page.getByTestId("retry-button")).toBeVisible();
});
