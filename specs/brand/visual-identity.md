# Visual Identity

Colors, typography, spacing tokens, and visual guidelines for Level8.

---

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Coral** | `#FF6B4A` | Primary accent, CTAs, key interactions |
| **Coral Dark** | `#E5533A` | Hover states, active elements |
| **Coral Light** | `#FF8A70` | Secondary highlights |

### Neutral Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Ink** | `#1A1A1A` | Primary text, headings |
| **Charcoal** | `#4A4A4A` | Secondary text, body copy |
| **Slate** | `#7A7A7A` | Tertiary text, captions, disabled icons |
| **Cloud** | `#E8E8E8` | Borders, dividers |
| **Mist** | `#F5F5F5` | Backgrounds, cards |
| **White** | `#FFFFFF` | Primary background |

### Semantic Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Success** | `#2ECC71` | Completed, positive feedback |
| **Warning** | `#F39C12` | Cautions, pending states |
| **Error** | `#E74C3C` | Errors, destructive actions |
| **Info** | `#3498DB` | Informational highlights |

### Color Ratios
- **70%** — Neutral backgrounds (White, Mist)
- **20%** — Text and structure (Ink, Charcoal, Cloud)
- **10%** — Accent (Coral family)

---

## Typography

### Font Stack

**Primary: Satoshi**
```css
font-family: 'Satoshi', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| **Display** | 48px / 3rem | Black (900) | 1.1 |
| **H1** | 36px / 2.25rem | Bold (700) | 1.2 |
| **H2** | 28px / 1.75rem | Bold (700) | 1.25 |
| **H3** | 22px / 1.375rem | Bold (700) | 1.3 |
| **H4** | 18px / 1.125rem | Medium (500) | 1.4 |
| **Body** | 16px / 1rem | Medium (500) | 1.6 |
| **Body Small** | 14px / 0.875rem | Medium (500) | 1.5 |
| **Caption** | 12px / 0.75rem | Medium (500) | 1.4 |
| **Button** | 14px / 0.875rem | Bold (700) | 1 |

---

## Spacing System

8px base grid:

| Token | Value | Use |
|-------|-------|-----|
| `space-xs` | 4px | Tight gaps, inline elements |
| `space-sm` | 8px | Related elements |
| `space-md` | 16px | Standard padding |
| `space-lg` | 24px | Section gaps |
| `space-xl` | 32px | Major sections |
| `space-2xl` | 48px | Page-level spacing |

---

## Iconography

- **Style:** Outlined, 2px stroke
- **Base size:** 24x24px (scales to 16px, 20px, 32px)
- **Corners:** Rounded (2px radius)
- **Source:** Lucide Icons base set
- **Colors:** Default Charcoal, Active Coral, Disabled Slate

---

## Components

### Cards
- Background: White
- Border: 1px Cloud
- Border-radius: 12px
- Padding: 20px
- Hover shadow: `0 2px 8px rgba(0,0,0,0.06)`

### Buttons
- Height: 44px (touch-friendly)
- Padding: 12px 24px
- Border-radius: 8px
- Primary: Coral background, White text
- Secondary: White background, Ink text, Charcoal border

---

## Accessibility

- All color combinations meet WCAG 2.1 AA
- Coral on White: Use for large text and icons only (4.0:1)
- Ink on White: Primary text choice (16:1+)
- Touch targets: minimum 44px
