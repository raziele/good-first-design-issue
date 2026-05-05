# Flow: Search and Filter Issues

User narrows down issues to find relevant opportunities.

## Entry Point
- User is on homepage/browse view
- Search bar and filter controls are visible

## Steps

### Search Path
1. User focuses search input
2. User types search query
3. System debounces input (300ms)
4. System executes search against title + description
5. Results update in real-time

### Filter Path
1. User clicks filter control
2. On desktop: dropdown/pill toggles appear inline
3. On mobile: bottom sheet slides up
4. User selects freshness option (Last 7 days, Last 30 days, Last 90 days, All time)
5. Results update immediately

### Combined
- Search and filter combine with AND logic
- Active filters shown as removable chips

## States

### Search Active
- Search input has focus ring
- Clear button (×) appears when text present
- Results count shown: "12 issues match"

### Filter Active
- Active filter shown as highlighted pill (Coral background)
- "Clear filters" link visible

### No Results
- Message: "No matches — try adjusting your filters or search terms."
- Suggestions: show popular/recent issues as fallback

### Mobile Bottom Sheet
- Slides up from bottom
- Shows freshness options as large tap targets (44px min)
- Apply/Clear buttons at bottom
- Swipe down or tap overlay to dismiss

## Edge Cases

- Search query too short (< 2 chars) → no search executed, show hint
- Special characters in search → escaped, search proceeds normally
- Filter + search returns 0 results → show combined empty state
