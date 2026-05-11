/**
 * RULE-ISS-002: IssueCard displays required preview information.
 * RULE-ISS-004: Claimed issues are marked with a visual indicator.
 */

import React from "react";

type ComplexityScore = "low" | "medium" | "high";
type SeniorityLevel = "junior" | "mid" | "senior";

type Issue = {
  id: string;
  repo_name: string;
  title: string;
  description_truncated: string;
  complexity_score: ComplexityScore;
  attractiveness_rating: number;
  seniority_level: SeniorityLevel;
  freshness_days: number;
  has_media: boolean;
  is_claimed: boolean;
  github_url: string;
};

type IssueCardProps = {
  issue: Issue;
};

export default function IssueCard({ issue }: IssueCardProps) {
  return (
    <div className="issue-card">
      <div className="issue-card__repo">{issue.repo_name}</div>
      <h3 className="issue-card__title">{issue.title}</h3>
      <p className="issue-card__description">{issue.description_truncated}</p>
      <div className="issue-card__meta">
        <span className="issue-card__complexity">{issue.complexity_score}</span>
        <span className="issue-card__seniority">{issue.seniority_level}</span>
        <span className="issue-card__freshness">{issue.freshness_days} days ago</span>
        <span className="issue-card__rating">{issue.attractiveness_rating}</span>
      </div>
      {issue.has_media && (
        <span data-testid="media-indicator" className="issue-card__media-indicator">
          📎
        </span>
      )}
      {issue.is_claimed && (
        <span className="issue-card__claimed-badge">Already claimed</span>
      )}
    </div>
  );
}
