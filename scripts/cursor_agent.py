"""Cursor agent CLI wrapper and helpers."""

import os
import subprocess
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_TIMEOUT = 900


def cursor_agent_run(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    cwd: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Run Cursor agent CLI and return its text output.

    Requires CURSOR_API_KEY env var.
    """
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("CURSOR_API_KEY not set")

    cmd = [
        "agent",
        "--api-key", api_key,
        "--model", model,
        "--output-format", "text",
        "--trust",
        "--force",
        "-p",
        prompt,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        stdin=subprocess.DEVNULL,
        cwd=cwd or str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cursor agent failed (exit {result.returncode}):\n{result.stderr}"
        )
    out = (result.stdout or "").strip()
    if not out:
        raise RuntimeError("cursor agent produced no output")
    return out


def load_agent_config(agent_name: str) -> dict:
    """Read agents/<name>/config.yaml and return as dict."""
    path = AGENTS_DIR / agent_name / "config.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_agent_prompt(agent_name: str, **kwargs: str) -> str:
    """Read agents/<name>/prompt.md with optional {{key}} substitution."""
    path = AGENTS_DIR / agent_name / "prompt.md"
    with open(path) as f:
        template = f.read()
    for key, value in kwargs.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template
