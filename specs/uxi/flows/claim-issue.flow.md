# Flow: Claim Issue

Designer signals intent to work on an issue.

## Entry Point
- User is on issue detail view
- Clicks "Claim This Task" button

## Steps

1. User clicks "Claim This Task" CTA
2. System displays claim options modal/sheet:
   - Option A: "Go to GitHub" (primary)
   - Option B: "Copy comment" (secondary)
3. User selects an option

### Path A: Go to GitHub
4a. System opens GitHub issue in new tab
5a. GitHub comment form is pre-filled with AI-generated claim comment
6a. User reviews and posts comment on GitHub

### Path B: Copy Comment
4b. System copies AI-generated claim comment to clipboard
5b. System shows confirmation: "Comment copied! Paste it on GitHub when you're ready."
6b. User can manually navigate to GitHub and paste

## States

### Claim Options Modal
- Title: "Ready to claim this task?"
- AI-generated comment preview shown
- Two action buttons: "Go to GitHub" (primary), "Copy comment" (secondary)
- Close/cancel option

### Clipboard Confirmation
- Toast notification: "Comment copied!"
- Auto-dismisses after 3 seconds

### Already Claimed Warning
- If issue has `is_claimed = true`:
  - Badge on detail view: "Already claimed"
  - Claim CTA still enabled (no blocking)
  - Optional subtle hint: "Someone may already be working on this"

## Edge Cases

- Clipboard API fails → show error: "Couldn't copy. Try selecting the text manually."
- Popup blocker prevents new tab → show fallback link: "Click here to open on GitHub"
- User claims from mobile → same flow, bottom sheet instead of modal
