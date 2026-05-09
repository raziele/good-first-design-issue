#!/usr/bin/env python3
"""Fail if any `raise NotImplementedError(...)` remains under src/backend/app.

Uses AST so docstrings / comments mentioning NotImplementedError are ignored.
See plans/stub-first-tdd-pipeline.md (strict post-codegen check).
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def _offenders(app_root: Path) -> list[str]:
    bad: list[str] = []
    for path in sorted(app_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, OSError) as e:
            bad.append(f"{path}: parse error: {e}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise) or node.exc is None:
                continue
            exc = node.exc
            if isinstance(exc, ast.Call):
                func = exc.func
                if isinstance(func, ast.Name) and func.id == "NotImplementedError":
                    bad.append(str(path))
                    break
            elif isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                bad.append(str(path))
                break
    return bad


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--app-root",
        type=Path,
        default=Path("src/backend/app"),
        help="app package root (default: src/backend/app)",
    )
    args = p.parse_args()
    root = args.app_root.resolve()
    if not root.is_dir():
        print(f"check_app_no_notimplemented: missing {root}", file=sys.stderr)
        return 0

    hits = _offenders(root)
    if not hits:
        return 0

    print("::error::NotImplementedError still raised in app package (stubs not fully implemented):", file=sys.stderr)
    for h in hits:
        print(f"  {h}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
