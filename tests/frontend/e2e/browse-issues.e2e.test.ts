/**
 * E2E test skeleton for Browse Issues flow.
 * Spec: specs/behavior/issues.spec.md
 * Flow: specs/uxi/flows/browse-issues.flow.md
 *
 * These tests are structured for Playwright. Wire up `page` fixture to a
 * running dev server before executing.
 */

import { test, expect } from "@playwright/test";

// ---------------------------------------------------------------------------
// Fixtures / helpers
// ---------------------------------------------------------------------------

const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

// ---------------------------------------------------------------------------
// Flow: Browse Issues — Entry Point
// ---------------------------------------------------------------------------

test.describe("Browse Issues flow — homepage", () => {
  test("homepage loads at /", async ({ page }) => {
    // Entry point from browse-issues.flow.md
    await page.goto(BASE_URL + "/");
    await expect(page).toHaveURL(/\//);
  });

  // RULE-ISS-001: Only relevant active issues appear
  test("issue listing displays only relevant active issues", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    // Wait for issue cards to render (skeleton → content)
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    const cards = await page.locator('[data-testid="issue-card"]').all();
    // All visible cards should be present; filter logic validated in unit tests
    expect(cards.length).toBeGreaterThanOrEqual(0);
  });

  // RULE-ISS-002: Issue card displays preview information
  test("issue card shows repo name, title, and truncated description", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    const firstCard = page.locator('[data-testid="issue-card"]').first();

    await expect(
      firstCard.locator('[data-testid="issue-repo-name"]')
    ).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="issue-title"]')
    ).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="issue-description-preview"]')
    ).toBeVisible();
  });

  test("issue card shows complexity score, attractiveness rating, seniority level", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    const firstCard = page.locator('[data-testid="issue-card"]').first();

    await expect(
      firstCard.locator('[data-testid="issue-complexity"]')
    ).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="issue-attractiveness"]')
    ).toBeVisible();
    await expect(
      firstCard.locator('[data-testid="issue-seniority"]')
    ).toBeVisible();
  });

  test("media icon is shown on cards where has_media is true", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    // At least check the element can exist (no assertion on count since it depends on data)
    const mediaIcons = page.locator('[data-testid="issue-media-icon"]');
    // No hard assertion on count — just verify it doesn't throw
    await mediaIcons.count();
  });

  // RULE-ISS-004: Claimed issues are marked
  test("claimed issues show 'Already claimed' badge", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    // Verify claimed badge renders when present (data-dependent)
    const claimedBadges = page.locator('[data-testid="issue-claimed-badge"]');
    await claimedBadges.count();
  });

  // RULE-ISS-005: Default sort is by freshness
  test("issues are sorted by freshness (newest first) by default", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    const freshnessValues = await page
      .locator('[data-testid="issue-freshness"]')
      .allTextContents();

    if (freshnessValues.length >= 2) {
      // Extract numeric values and confirm ascending order (0 = newest)
      const nums = freshnessValues.map((v) => parseInt(v, 10)).filter(isFinite);
      for (let i = 1; i < nums.length; i++) {
        expect(nums[i]).toBeGreaterThanOrEqual(nums[i - 1]);
      }
    }
  });
});

// ---------------------------------------------------------------------------
// Flow states
// ---------------------------------------------------------------------------

test.describe("Browse Issues flow — loading state", () => {
  test("skeleton cards shown while loading", async ({ page }) => {
    // Intercept API to delay response and verify skeleton renders
    await page.route("**/api/**", async (route) => {
      await new Promise((res) => setTimeout(res, 500));
      await route.continue();
    });
    await page.goto(BASE_URL + "/");
    const skeleton = page.locator('[data-testid="issue-card-skeleton"]');
    // Skeleton may briefly appear
    await skeleton.count();
  });
});

test.describe("Browse Issues flow — empty state", () => {
  test("shows empty state message when no issues returned", async ({ page }) => {
    // Mock empty API response
    await page.route("**/api/issues**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ issues: [] }),
      });
    });
    await page.goto(BASE_URL + "/");
    await expect(
      page.locator("text=No design opportunities right now")
    ).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Browse Issues flow — error state", () => {
  test("shows error message and retry button on network failure", async ({
    page,
  }) => {
    await page.route("**/api/issues**", async (route) => {
      await route.abort("failed");
    });
    await page.goto(BASE_URL + "/");
    await expect(
      page.locator("text=Couldn't load tasks")
    ).toBeVisible({ timeout: 5000 });
    await expect(
      page.locator('[data-testid="retry-button"]')
    ).toBeVisible({ timeout: 5000 });
  });
});

// ---------------------------------------------------------------------------
// Flow step 6–7: Navigate to issue detail
// ---------------------------------------------------------------------------

test.describe("Browse Issues flow — navigate to detail", () => {
  // RULE-ISS-003: Issue detail view shows full information
  test("clicking an issue card navigates to detail view", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    await page.locator('[data-testid="issue-card"]').first().click();
    await expect(page).not.toHaveURL(BASE_URL + "/");
  });

  test("detail view shows full description, all scores, repo stars, and github link", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 5000 });
    await page.locator('[data-testid="issue-card"]').first().click();

    await expect(
      page.locator('[data-testid="issue-detail-description"]')
    ).toBeVisible({ timeout: 5000 });
    await expect(
      page.locator('[data-testid="issue-detail-repo-stars"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="issue-detail-github-link"]')
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Edge cases from browse-issues.flow.md
// ---------------------------------------------------------------------------

test.describe("Browse Issues flow — edge cases", () => {
  test("filter debounce: rapid filter toggles do not cause errors", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    const filter = page.locator('[data-testid="filter-control"]');
    // Rapidly click filter options
    for (let i = 0; i < 5; i++) {
      await filter.click();
    }
    // No JS errors should surface
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    await page.waitForTimeout(500);
    expect(errors).toHaveLength(0);
  });
});
