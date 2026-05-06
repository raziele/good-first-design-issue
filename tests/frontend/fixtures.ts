/**
 * Shared test fixtures for frontend unit tests.
 * Mirrors domain model from specs/chapters/domain-model.md (ENTITY-001: Issue)
 */

export interface Issue {
  id: string;
  github_url: string;
  repo_name: string;
  repo_stars: number;
  title: string;
  description: string;
  description_truncated: string;
  labels: string[];
  has_media: boolean;
  created_at: string;
  updated_at: string;
  freshness_days: number;
  classification: "relevant" | "not_relevant";
  is_claimed: boolean;
  complexity_score: "low" | "medium" | "high";
  attractiveness_rating: number;
  seniority_level: "junior" | "senior";
  status: "active" | "closed" | "archived";
  fetched_at: string;
}

export function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-001",
    github_url: "https://github.com/owner/repo/issues/1",
    repo_name: "owner/repo",
    repo_stars: 500,
    title: "Create wireframes for settings page",
    description:
      "We need mockup, user flow, and Figma designs for the new settings page.",
    description_truncated:
      "We need mockup, user flow, and Figma designs for the new settings page.",
    labels: ["design", "good first issue"],
    has_media: false,
    created_at: "2026-04-20T00:00:00Z",
    updated_at: "2026-04-21T00:00:00Z",
    freshness_days: 16,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.75,
    seniority_level: "junior",
    status: "active",
    fetched_at: "2026-05-06T00:00:00Z",
    ...overrides,
  };
}
