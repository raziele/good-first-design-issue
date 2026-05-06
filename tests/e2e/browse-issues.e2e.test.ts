/**
 * E2E skeleton: Browse Issues flow.
 *
 * UXI Flow: specs/uxi/flows/browse-issues.flow.md
 * Behavior: specs/behavior/issues.spec.md (RULE-ISS-001 through RULE-ISS-005)
 *
 * Wire these tests up by setting PLAYWRIGHT_BASE_URL to the running app.
 * Until the app is deployed, each test body is marked TODO.
 */

import { test, expect } from "@playwright/test";

// ---------------------------------------------------------------------------
// Browse Issues — Flow steps (browse-issues.flow.md)
// ---------------------------------------------------------------------------

test.describe("Browse Issues flow", () => {
  test.beforeEach(async ({ page }) => {
    // Entry point: homepage (/)
    await page.goto("/");
  });

  // Step 1-2: landing + issue listing displayed
  test("browse_issues_landing_shows_issue_listing", async ({ page }) => {
    // TODO: Seed database with at least one relevant active issue before running.
    await expect(page.locator("[data-testid='issue-card']").first()).toBeVisible();
  });

  // Loading state
  test("browse_issues_shows_skeleton_cards_while_loading", async ({ page }) => {
    // TODO: Throttle network to observe loading state
    // Skeleton cards should be visible before data arrives
    // await page.route("**/api/issues", route => route.fulfill({ delay: 500, body: "[]", contentType: "application/json" }));
    // await expect(page.locator("[data-testid='skeleton-card']")).toBeVisible();
    test.skip(true, "TODO: Implement with network throttle fixture");
  });

  // Step 4: search (RULE-SRC-001)
  test("browse_issues_search_filters_listing_in_real_time", async ({ page }) => {
    // TODO: Seed issue with title "Mobile onboarding redesign"
    const searchInput = page.locator("[data-testid='search-input']");
    await searchInput.fill("onboarding");
    await expect(page.locator("[data-testid='issue-card']")).toHaveCount(1);
  });

  // Step 5: freshness filter (RULE-SRC-002)
  test("browse_issues_freshness_filter_narrows_results", async ({ page }) => {
    // TODO: Seed issues with varying freshness
    const filterButton = page.locator("[data-testid='filter-button']");
    await filterButton.click();
    await page.locator("text=Last 7 days").click();
    // All visible cards should be from the last 7 days
    // TODO: Assert via data attribute or text
    test.skip(true, "TODO: Add freshness_days data attribute to cards for assertion");
  });

  // Step 6-7: click card → detail view
  test("browse_issues_clicking_card_navigates_to_detail", async ({ page }) => {
    // TODO: Seed at least one issue
    const firstCard = page.locator("[data-testid='issue-card']").first();
    await firstCard.click();
    await expect(page).toHaveURL(/\/issues\//);
  });

  // Empty state — no results
  test("browse_issues_empty_state_shows_correct_message", async ({ page }) => {
    const searchInput = page.locator("[data-testid='search-input']");
    await searchInput.fill("blockchain_xyz_impossible_query");
    const emptyMsg = page.locator("text=No matches");
    await expect(emptyMsg).toBeVisible();
  });

  // Empty state — no issues at all
  test("browse_issues_empty_database_shows_no_opportunities_message", async ({ page }) => {
    // TODO: Run against a clean database
    // await expect(page.locator("text=No design opportunities right now")).toBeVisible();
    test.skip(true, "TODO: Requires clean-DB fixture");
  });

  // Error state
  test("browse_issues_error_state_shows_retry_option", async ({ page }) => {
    // TODO: Intercept API and return 500
    // await page.route("**/api/issues", route => route.fulfill({ status: 500 }));
    // await page.reload();
    // await expect(page.locator("text=Couldn't load tasks")).toBeVisible();
    // await expect(page.locator("[data-testid='retry-button']")).toBeVisible();
    test.skip(true, "TODO: Implement with API route intercept");
  });

  // Edge case: long title truncated
  test("browse_issues_long_title_is_truncated_with_ellipsis", async ({ page }) => {
    // TODO: Seed issue with 200+ character title
    // Card should show truncated title with ellipsis (CSS line-clamp)
    test.skip(true, "TODO: Seed long-title issue fixture");
  });

  // RULE-ISS-005: default sort freshness
  test("browse_issues_default_sort_shows_newest_first", async ({ page }) => {
    // TODO: Seed two issues with different freshness; assert order in DOM
    test.skip(true, "TODO: Seed ordered fixture");
  });

  // RULE-ISS-002: card shows required fields
  test("browse_issues_card_displays_required_fields", async ({ page }) => {
    // TODO: Seed one full issue
    const card = page.locator("[data-testid='issue-card']").first();
    await expect(card.locator("[data-testid='repo-name']")).toBeVisible();
    await expect(card.locator("[data-testid='issue-title']")).toBeVisible();
    await expect(card.locator("[data-testid='complexity-score']")).toBeVisible();
    await expect(card.locator("[data-testid='seniority-level']")).toBeVisible();
  });

  // RULE-ISS-004: claimed issue shows badge
  test("browse_issues_claimed_issue_shows_already_claimed_badge", async ({ page }) => {
    // TODO: Seed issue with is_claimed=true
    // await expect(page.locator("text=Already claimed")).toBeVisible();
    test.skip(true, "TODO: Seed claimed issue fixture");
  });
});
