import { describe, expect, it } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { MobileFreshnessTray } from "../../../src/frontend/src/search/MobileFreshnessTray.jsx";

describe("RULE-SRC-004 mobile filter chrome", () => {
  it("uses a viewport-anchored surface for handset filter picks", () => {
    const markup = renderToStaticMarkup(
      createElement(MobileFreshnessTray, {
        open: true,
        selectedSlug: "last_7_days",
      }),
    );
    expect(markup).toContain("Last 7 days");
    expect(markup.includes("viewport-bottom") || markup.includes('data-sheet="mobile-filters"')).toBe(true);
  });
});
