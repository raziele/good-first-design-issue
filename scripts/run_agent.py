#!/usr/bin/env python3
"""Generic agent runner — invokes a named agent via the Cursor CLI.

Usage: python scripts/run_agent.py <agent-name> [--extra-context <text>]
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

from cursor_agent import (
    PROJECT_ROOT,
    DEFAULT_MODEL,
    cursor_agent_run,
    load_agent_config,
    load_agent_prompt,
)

LOCKS_PATH = PROJECT_ROOT / "pipeline" / "locks.yaml"


def load_scope_preamble(agent_name: str) -> str:
    """Build a scope-restriction preamble from pipeline/locks.yaml."""
    with open(LOCKS_PATH) as f:
        locks = yaml.safe_load(f)

    perms = locks.get("permissions", {}).get(agent_name)
    if not perms:
        return ""

    lines = [
        "IMPORTANT — FILESYSTEM SCOPE RESTRICTIONS:",
        f"  You may ONLY write to: {', '.join(perms.get('write', []))}",
        f"  You may read: {', '.join(perms.get('read', []))}",
        f"  You must NOT modify: {', '.join(perms.get('deny', []))}",
        "Any out-of-scope file modification will be rejected.\n",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run a Cursor-backed agent")
    parser.add_argument("agent_name", help="Agent directory name (e.g. agent-1-testgen)")
    parser.add_argument("--extra-context", default="", help="Additional context appended to the prompt")
    parser.add_argument("--extra-context-file", default="", help="Path to file whose contents are appended as extra context")
    args = parser.parse_args()

    config = load_agent_config(args.agent_name)
    # Resolution order: CURSOR_MODEL env var (project-level, set by workflow)
    # > per-agent config override > built-in default.
    model = (
        os.environ.get("CURSOR_MODEL", "").strip()
        or config.get("model")
        or DEFAULT_MODEL
    )

    prompt = load_agent_prompt(args.agent_name)
    scope = load_scope_preamble(args.agent_name)
    if scope:
        prompt = scope + "\n" + prompt
    extra = args.extra_context
    if args.extra_context_file:
        extra = Path(args.extra_context_file).read_text()
    if extra:
        prompt += "\n\n--- ADDITIONAL CONTEXT ---\n" + extra

    print(f"Running {args.agent_name} with model={model}", file=sys.stderr)
    try:
        output = cursor_agent_run(prompt, model=model)
    except RuntimeError as exc:
        print(f"Agent failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(output)


if __name__ == "__main__":
    main()
