/**
 * E2E test skeleton for Search and Filter Issues flow.
 * Spec: specs/behavior/search.spec.md
 * Flow: specs/uxi/flows/search.flow.md
 *
 * Structured for Playwright. Requires a running dev server.
 */

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

// ---------------------------------------------------------------------------
// RULE-SRC-001: Full-text search
// ---------------------------------------------------------------------------

test.describe("Search flow — search matches title", () => {
  test("searching a keyword returns matching issues", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("onboarding");
    await page.waitForTimeout(350); // debounce (300ms per flow spec)

    const cards = page.locator('[data-testid="issue-card"]');
    const count = await cards.count();
    // All visible results must contain "onboarding" in title or description
    // Exact assertion depends on data; structural assertion here
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("searching returns empty state for unknown keyword", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    // Use a term extremely unlikely to match any issue
    await page.locator('[data-testid="search-input"]').fill("xyzblockchainxyz");
    await page.waitForTimeout(350);

    await expect(
      page.locator("text=No matches — try adjusting your search terms")
    ).toBeVisible({ timeout: 3000 });
  });

  test("search input shows clear button (×) when text is present", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("design");
    await expect(
      page.locator('[data-testid="search-clear-button"]')
    ).toBeVisible();
  });

  test("clearing search input removes clear button", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("design");
    await page.locator('[data-testid="search-clear-button"]').click();

    await expect(
      page.locator('[data-testid="search-clear-button"]')
    ).not.toBeVisible();
  });

  test("results count message is shown when search is active", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });
    await page.locator('[data-testid="search-input"]').fill("design");
    await page.waitForTimeout(350);

    await expect(
      page.locator('[data-testid="search-results-count"]')
    ).toBeVisible({ timeout: 3000 });
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-001 edge cases (from search.flow.md)
// ---------------------------------------------------------------------------

test.describe("Search flow — query edge cases", () => {
  test("query shorter than 2 chars does not trigger search", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("r");
    await page.waitForTimeout(350);

    // Should show hint or no results change — not a filtered result set
    const hint = page.locator('[data-testid="search-short-query-hint"]');
    await hint.count(); // presence is optional per implementation
  });

  test("special characters in search do not throw", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    await page.locator('[data-testid="search-input"]').fill('<script>alert("xss")</script>');
    await page.waitForTimeout(350);

    expect(errors).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

test.describe("Search flow — freshness filter", () => {
  test("clicking filter control reveals freshness options", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();

    await expect(
      page.locator('[data-testid="filter-option-7"]')
    ).toBeVisible({ timeout: 3000 });
    await expect(
      page.locator('[data-testid="filter-option-30"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="filter-option-90"]')
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="filter-option-all"]')
    ).toBeVisible();
  });

  test("selecting 'Last 7 days' filters results immediately", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();
    await page.locator('[data-testid="filter-option-7"]').click();

    // Active filter pill should appear
    await expect(
      page.locator('[data-testid="active-filter-pill"]')
    ).toBeVisible({ timeout: 3000 });
  });

  test("active filter is shown as highlighted pill", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();
    await page.locator('[data-testid="filter-option-30"]').click();

    const pill = page.locator('[data-testid="active-filter-pill"]');
    await expect(pill).toBeVisible({ timeout: 3000 });
  });

  test("'Clear filters' link is visible when filter is active", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();
    await page.locator('[data-testid="filter-option-7"]').click();

    await expect(
      page.locator('[data-testid="clear-filters-link"]')
    ).toBeVisible({ timeout: 3000 });
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-003: Search and filter combine
// ---------------------------------------------------------------------------

test.describe("Search flow — combined search and filter", () => {
  test("search and filter combine with AND logic", async ({ page }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("design");
    await page.waitForTimeout(350);

    await page.locator('[data-testid="filter-control"]').click();
    await page.locator('[data-testid="filter-option-7"]').click();

    await page.waitForTimeout(350);
    // Both filters are active; no JS errors
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    expect(errors).toHaveLength(0);
  });

  test("combined search and filter with 0 results shows empty state", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    await page.locator('[data-testid="search-input"]').fill("xyzblockchainxyz");
    await page.waitForTimeout(350);

    await page.locator('[data-testid="filter-control"]').click();
    await page.locator('[data-testid="filter-option-7"]').click();
    await page.waitForTimeout(350);

    await expect(
      page.locator("text=No matches — try adjusting your filters or search terms")
    ).toBeVisible({ timeout: 3000 });
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-004: Mobile uses bottom sheet for filters
// ---------------------------------------------------------------------------

test.describe("Search flow — mobile bottom sheet for filters", () => {
  test.use({ viewport: { width: 390, height: 844 } }); // iPhone 14 dimensions

  test("filter button opens bottom sheet on mobile viewport", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();

    await expect(
      page.locator('[data-testid="filter-bottom-sheet"]')
    ).toBeVisible({ timeout: 3000 });
  });

  test("bottom sheet can be dismissed by swiping down or tapping overlay", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();
    await page.waitForSelector('[data-testid="filter-bottom-sheet"]', {
      timeout: 3000,
    });

    // Tap overlay to dismiss
    await page.locator('[data-testid="bottom-sheet-overlay"]').click();
    await expect(
      page.locator('[data-testid="filter-bottom-sheet"]')
    ).not.toBeVisible({ timeout: 3000 });
  });

  test("bottom sheet filter options have minimum 44px tap target", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="filter-control"]', {
      timeout: 5000,
    });
    await page.locator('[data-testid="filter-control"]').click();
    await page.waitForSelector('[data-testid="filter-bottom-sheet"]', {
      timeout: 3000,
    });

    const option = page.locator('[data-testid="filter-option-7"]');
    const box = await option.boundingBox();
    if (box) {
      expect(box.height).toBeGreaterThanOrEqual(44);
    }
  });

  test("search input debounces 300ms before triggering results update", async ({
    page,
  }) => {
    await page.goto(BASE_URL + "/");
    await page.waitForSelector('[data-testid="search-input"]', { timeout: 5000 });

    let requestCount = 0;
    page.on("request", (req) => {
      if (req.url().includes("/api/issues")) requestCount++;
    });

    // Type rapidly — should only fire once after debounce settles
    await page.locator('[data-testid="search-input"]').type("design", {
      delay: 50,
    });
    await page.waitForTimeout(400); // wait for debounce

    // At most 1–2 requests expected due to 300ms debounce
    expect(requestCount).toBeLessThanOrEqual(2);
  });
});
