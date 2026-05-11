/**
 * RULE-CLM-001: Claim action offers two options (Go to GitHub / Copy comment).
 * RULE-CLM-002: Claim comment is AI-generated (contextual, passed via props).
 */

import React from "react";

type ClaimIssue = {
  id: string;
  title: string;
  github_url: string;
  claim_comment: string;
};

type ClaimModalProps = {
  issue: ClaimIssue;
  onClose: () => void;
};

export default function ClaimModal({ issue, onClose }: ClaimModalProps) {
  return (
    <div className="claim-modal" role="dialog" aria-modal="true">
      <div className="claim-modal__header">
        <h2>Ready to claim this task?</h2>
        <button
          data-testid="modal-close"
          className="claim-modal__close"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>
      </div>
      <div className="claim-modal__body">
        <p className="claim-modal__title">{issue.title}</p>
        <div className="claim-modal__comment-preview">
          <p>{issue.claim_comment}</p>
        </div>
      </div>
      <div className="claim-modal__actions">
        <a
          data-testid="go-to-github"
          href={issue.github_url}
          target="_blank"
          rel="noopener noreferrer"
          className="claim-modal__btn claim-modal__btn--primary"
        >
          Go to GitHub
        </a>
        <button
          data-testid="copy-comment"
          className="claim-modal__btn claim-modal__btn--secondary"
          onClick={() => navigator.clipboard?.writeText(issue.claim_comment)}
        >
          Copy comment
        </button>
      </div>
    </div>
  );
}
