#!/usr/bin/env python3
"""
AI-First TDD Pipeline Orchestrator

Coordinates the three-agent workflow:
1. Detect spec changes
2. Run Agent 1 (test generation) if specs changed
3. Run baseline tests
4. Run Agent 2 (code generation) to fix failures
5. Run Agent 3 (review) to validate changes
6. Merge or flag for human review
"""

import subprocess
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "pipeline" / "reports"


def detect_spec_changes() -> bool:
    """Check if specs/ has changed since last run."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "--", "specs/"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    return bool(result.stdout.strip())


def run_tests() -> dict:
    """Run the full test suite and return results."""
    # TODO: Implement test runner invocation
    # Should run both backend (pytest) and frontend (vitest) tests
    return {"passed": 0, "failed": 0, "errors": []}


def run_agent(agent_name: str, extra_context: str = "") -> dict:
    """Run a named agent via scripts/run_agent.py and return results."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "run_agent.py"),
        agent_name,
    ]
    if extra_context:
        cmd += ["--extra-context", extra_context]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=960,  # 900 agent timeout + 60s buffer
        cwd=PROJECT_ROOT,
    )
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "agent": agent_name,
        "output": result.stdout,
        "stderr": result.stderr,
    }


def validate_file_scope(agent_name: str) -> bool:
    """Run scripts/validate_scope.sh to check the agent stayed in scope."""
    result = subprocess.run(
        [str(PROJECT_ROOT / "scripts" / "validate_scope.sh"), agent_name],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        print(f"Scope violation: {result.stdout}{result.stderr}", file=sys.stderr)
    return result.returncode == 0


def generate_report(run_id: str, results: dict) -> Path:
    """Write a structured report to pipeline/reports/."""
    report_path = REPORTS_DIR / f"report-{run_id}.json"
    report_path.write_text(json.dumps(results, indent=2))
    return report_path


def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"Pipeline run: {run_id}")

    # Step 1: Detect changes
    specs_changed = detect_spec_changes()
    print(f"Spec changes detected: {specs_changed}")

    # Step 2: Run Agent 1 if specs changed
    if specs_changed:
        print("Running Agent 1 (Test Generator)...")
        run_agent("agent-1-testgen")

    # Step 3: Baseline test run
    print("Running baseline tests...")
    baseline = run_tests()

    if baseline["failed"] == 0 and not specs_changed:
        print("All tests pass, no spec changes. Nothing to do.")
        return

    # Step 4: Run Agent 2 (Code Generator)
    print("Running Agent 2 (Code Generator)...")
    run_agent("agent-2-codegen")

    # Step 5: Verify tests pass
    print("Running post-codegen tests...")
    final = run_tests()

    # Step 6: Run Agent 3 (Review)
    print("Running Agent 3 (Reviewer)...")
    review = run_agent("agent-3-review")

    # Step 7: Generate report
    report = generate_report(run_id, {
        "run_id": run_id,
        "specs_changed": specs_changed,
        "baseline_tests": baseline,
        "final_tests": final,
        "review": review,
    })
    print(f"Report written to: {report}")


if __name__ == "__main__":
    main()
