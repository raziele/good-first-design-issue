# Flow: Browse Issues

Entry point for designers discovering design opportunities.

## Entry Point
- URL: `/` (homepage)
- Direct navigation or external link

## Steps

1. User lands on homepage
2. System displays issue listing (cards in grid/list layout)
3. User scrolls through issues
4. User optionally enters search query
5. User optionally applies freshness filter
6. User clicks on an issue card
7. System navigates to issue detail view

## States

### Loading
- Skeleton cards displayed while fetching issues
- Search/filter controls visible but disabled

### Empty (no results)
- Message: "No matches — try adjusting your filters or search terms."
- Clear filters button visible

### Empty (no issues at all)
- Message: "No design opportunities right now. Check back soon!"
- Note: This state should be rare given daily ETL

### Success
- Issue cards displayed in grid (desktop) or single column (mobile)
- Default sort: freshness (newest first)
- Card shows: repo, title, truncated description, scores, media indicator

### Error
- Message: "Couldn't load tasks. Check your connection and try again."
- Retry button visible

## Edge Cases

- Extremely long issue title → truncate with ellipsis after 2 lines
- User rapidly toggles filters → debounce filter requests (300ms)
- Network timeout → show error state, preserve last filter state for retry
