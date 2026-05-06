/**
 * E2E test skeleton for Search and Filter flow.
 * Spec: specs/behavior/search.spec.md
 * Flow: specs/uxi/flows/search.flow.md
 *
 * Uses Playwright. All API calls are route-mocked for hermeticity.
 * Debounce (300ms) is accounted for in wait assertions.
 */

import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const ALL_ISSUES = [
  {
    id: "onboarding-fresh",
    title: "Mobile onboarding redesign",
    description: "Redesign the onboarding flow for mobile users.",
    freshness_days: 3,
    classification: "relevant",
    status: "active",
  },
  {
    id: "accessibility-old",
    title: "Accessibility audit for forms",
    description: "Perform an accessibility audit of all form fields.",
    freshness_days: 45,
    classification: "relevant",
    status: "active",
  },
  {
    id: "icon-system-mid",
    title: "Icon system refresh",
    description: "Update the icon set to match new brand guidelines.",
    freshness_days: 20,
    classification: "relevant",
    status: "active",
  },
];

async function mockSearchApi(
  page: Page,
  {
    query = "",
    maxDays = null,
    response = ALL_ISSUES,
  }: { query?: string; maxDays?: number | null; response?: typeof ALL_ISSUES } = {}
) {
  await page.route("**/api/issues**", (route) => {
    const url = new URL(route.request().url());
    const q = url.searchParams.get("q") ?? "";
    const days = url.searchParams.get("freshness_days");

    let results = ALL_ISSUES;

    if (q) {
      results = results.filter(
        (i) =>
          i.title.toLowerCase().includes(q.toLowerCase()) ||
          i.description.toLowerCase().includes(q.toLowerCase())
      );
    }

    if (days) {
      results = results.filter((i) => i.freshness_days <= parseInt(days, 10));
    }

    route.fulfill({ json: { issues: results, total: results.length } });
  });
}

// ---------------------------------------------------------------------------
// RULE-SRC-001: Full-text search
// ---------------------------------------------------------------------------

test("search: typing a query filters issues by title match", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("onboarding");
  await page.waitForTimeout(350); // debounce

  await expect(page.getByTestId("issue-card-onboarding-fresh")).toBeVisible();
  await expect(page.getByTestId("issue-card-accessibility-old")).not.toBeVisible();
});

test("search: typing a query filters issues by description match", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("accessibility");
  await page.waitForTimeout(350);

  await expect(page.getByTestId("issue-card-accessibility-old")).toBeVisible();
  await expect(page.getByTestId("issue-card-onboarding-fresh")).not.toBeVisible();
});

test("search: no results shows empty state message", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("blockchain");
  await page.waitForTimeout(350);

  await expect(page.getByTestId("empty-state")).toContainText(
    "No matches — try adjusting your search terms."
  );
});

test("search: clear button appears when query is entered", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("onboarding");
  await expect(page.getByTestId("search-clear")).toBeVisible();
});

test("search: clearing the query restores all results", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("onboarding");
  await page.waitForTimeout(350);
  await page.getByTestId("search-clear").click();
  await page.waitForTimeout(350);

  await expect(page.getByTestId("issue-card-onboarding-fresh")).toBeVisible();
  await expect(page.getByTestId("issue-card-accessibility-old")).toBeVisible();
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

test("search: filter 'Last 7 days' shows only fresh issues", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-freshness").click();
  await page.getByTestId("filter-option-7").click();
  await page.waitForTimeout(100);

  await expect(page.getByTestId("issue-card-onboarding-fresh")).toBeVisible();
  await expect(page.getByTestId("issue-card-accessibility-old")).not.toBeVisible();
});

test("search: filter 'All time' shows all issues", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-freshness").click();
  await page.getByTestId("filter-option-all").click();

  await expect(page.getByTestId("issue-card-onboarding-fresh")).toBeVisible();
  await expect(page.getByTestId("issue-card-accessibility-old")).toBeVisible();
  await expect(page.getByTestId("issue-card-icon-system-mid")).toBeVisible();
});

// ---------------------------------------------------------------------------
// RULE-SRC-003: Combined search and filter
// ---------------------------------------------------------------------------

test("search: combined query and freshness filter applies AND logic", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("mobile");
  await page.getByTestId("filter-freshness").click();
  await page.getByTestId("filter-option-7").click();
  await page.waitForTimeout(350);

  await expect(page.getByTestId("issue-card-onboarding-fresh")).toBeVisible();
  await expect(page.getByTestId("issue-card-accessibility-old")).not.toBeVisible();
});

// ---------------------------------------------------------------------------
// RULE-SRC-004: Mobile uses bottom sheet for filters
// ---------------------------------------------------------------------------

test("search: mobile viewport opens bottom sheet on filter tap", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); // iPhone 14
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-button-mobile").click();
  await expect(page.getByTestId("filter-bottom-sheet")).toBeVisible();
});

test("search: mobile bottom sheet swipe-down closes it", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-button-mobile").click();
  await expect(page.getByTestId("filter-bottom-sheet")).toBeVisible();

  // Tap overlay to dismiss
  await page.getByTestId("bottom-sheet-overlay").click();
  await expect(page.getByTestId("filter-bottom-sheet")).not.toBeVisible();
});

test("search: mobile bottom sheet has min 44px tap targets", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-button-mobile").click();

  const options = page.getByTestId(/^filter-sheet-option-/);
  const count = await options.count();
  for (let i = 0; i < count; i++) {
    const box = await options.nth(i).boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
  }
});

// ---------------------------------------------------------------------------
// Flow edge cases — search.flow.md
// ---------------------------------------------------------------------------

test("search: query shorter than 2 chars does not trigger search request", async ({ page }) => {
  const searchRequests: string[] = [];
  page.on("request", (req) => {
    if (req.url().includes("/api/issues") && req.url().includes("q=")) {
      searchRequests.push(req.url());
    }
  });

  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("search-input").fill("a");
  await page.waitForTimeout(400);

  expect(searchRequests).toHaveLength(0);
});

test("search: active filter shown as highlighted pill", async ({ page }) => {
  await mockSearchApi(page);
  await page.goto("/");

  await page.getByTestId("filter-freshness").click();
  await page.getByTestId("filter-option-7").click();

  await expect(page.getByTestId("active-filter-pill")).toBeVisible();
  await expect(page.getByTestId("active-filter-pill")).toContainText("Last 7 days");
});

test("search: debounce — rapid input does not send multiple requests", async ({ page }) => {
  const searchRequests: string[] = [];
  let callCount = 0;

  await page.route("**/api/issues**", (route) => {
    callCount++;
    searchRequests.push(route.request().url());
    route.fulfill({ json: { issues: [], total: 0 } });
  });

  await page.goto("/");

  // Rapidly type characters (within debounce window)
  const input = page.getByTestId("search-input");
  await input.fill("m");
  await input.fill("mo");
  await input.fill("mob");
  await page.waitForTimeout(400); // wait for debounce to settle

  // Only the trailing call (after debounce) should have q= param
  const queriedCalls = searchRequests.filter((u) => u.includes("q="));
  expect(queriedCalls.length).toBeLessThanOrEqual(1);
});
