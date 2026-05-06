/**
 * Shared test fixtures for frontend unit and component tests.
 * Mirrors ENTITY-001 from specs/chapters/domain-model.md.
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
    github_url: "https://github.com/org/repo/issues/1",
    repo_name: "org/repo",
    repo_stars: 1200,
    title: "Design new onboarding flow",
    description:
      "We need a full UX redesign of the onboarding. Figma mockups welcome.",
    description_truncated:
      "We need a full UX redesign of the onboarding. Figma mockups welcome.",
    labels: ["design", "ux"],
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
