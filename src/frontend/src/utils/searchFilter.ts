/**
 * RULE-SRC-001/002/003: Client-side search + freshness filter with AND logic.
 */

type Issue = {
  id: string;
  title: string;
  description: string;
  freshness_days: number;
  [key: string]: unknown;
};

type FilterOptions = {
  query?: string;
  freshnessFilter?: string;
};

const FRESHNESS_MAP: Record<string, number> = {
  last_7_days: 7,
  last_30_days: 30,
  last_90_days: 90,
};

export function applySearchAndFilter<T extends Issue>(
  issues: T[],
  { query = "", freshnessFilter = "all_time" }: FilterOptions = {}
): T[] {
  let result = issues;

  if (query) {
    const q = query.toLowerCase();
    result = result.filter(
      (i) =>
        i.title.toLowerCase().includes(q) ||
        i.description.toLowerCase().includes(q)
    );
  }

  if (freshnessFilter && freshnessFilter !== "all_time") {
    const maxDays = FRESHNESS_MAP[freshnessFilter];
    if (maxDays !== undefined) {
      result = result.filter((i) => i.freshness_days <= maxDays);
    }
  }

  return result;
}
