#!/usr/bin/env python3
"""Generate minimal SUT stubs under src/backend/app from backend test imports.

MVP (see plans/stub-first-tdd-pipeline.md):
- Only ``from app.<module path> import <names>`` (no ``from app import ...``, no ``*``).
- Only **function** stubs: imported names must start with a lowercase letter.
- Creates / merges ``def name(*args, **kwargs): raise NotImplementedError(STUB_MSG)``.
- Idempotent: does not overwrite non-stub implementations.

Exit 1 on unsupported patterns with a clear message.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Iterable

STUB_MSG = "SUT stub — implement in agent-2-codegen"


class StubGenError(Exception):
    pass


def _iter_test_files(tests_root: Path) -> Iterable[Path]:
    if not tests_root.is_dir():
        return
    for p in sorted(tests_root.rglob("*.py")):
        if "contract" in p.parts:
            continue
        yield p


def _ensure_pkg_inits(app_root: Path, py_file: Path) -> None:
    """Create package __init__.py files for parent dirs under app_root."""
    try:
        rel = py_file.relative_to(app_root)
    except ValueError:
        return
    # parents: ... -> claim.py, services, .
    for parent in list(rel.parents)[:-1]:
        if str(parent) == ".":
            continue
        init_dir = app_root / parent
        init_py = init_dir / "__init__.py"
        if not init_py.exists():
            init_dir.mkdir(parents=True, exist_ok=True)
            init_py.write_text(
                '"""Package (auto-created for SUT stub path)."""\n',
                encoding="utf-8",
            )


def module_suffix_to_path(app_root: Path, suffix: str) -> Path:
    """Map ``claim`` or ``services.claim`` → ``app/claim.py`` or ``app/services/claim.py``."""
    parts = suffix.split(".")
    if not parts or any(not p or not p.isidentifier() for p in parts):
        raise StubGenError(f"Invalid app module suffix {suffix!r}")
    if len(parts) == 1:
        return app_root / f"{parts[0]}.py"
    return app_root.joinpath(*parts[:-1]) / f"{parts[-1]}.py"


def collect_required_stubs(tests_root: Path) -> dict[str, set[str]]:
    """Return mapping ``module_suffix`` (e.g. ``services.claim``) → function names."""
    per_suffix: dict[str, set[str]] = {}
    for test_path in _iter_test_files(tests_root):
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                if not mod.startswith("app."):
                    continue
                if mod == "app":
                    raise StubGenError(
                        f"{test_path}: `from app import ...` is not supported in stub MVP — "
                        f"use `from app.<module> import <name>`."
                    )
                suffix = mod[len("app.") :]
                for alias in node.names:
                    name = alias.name
                    if name == "*":
                        raise StubGenError(
                            f"{test_path}: `from app.{suffix} import *` is not supported in stub MVP."
                        )
                    if name[:1].isupper():
                        raise StubGenError(
                            f"{test_path}: imported `{name}` from `{mod}` looks like a class; "
                            f"class stubs are Phase 1b — use lowercase factory functions for now."
                        )
                    per_suffix.setdefault(suffix, set()).add(name)
    return per_suffix


def _is_stub_function(node: ast.FunctionDef) -> bool:
    if len(node.body) != 1:
        return False
    stmt = node.body[0]
    if not isinstance(stmt, ast.Raise) or not isinstance(stmt.exc, ast.Call):
        return False
    func = stmt.exc.func
    return isinstance(func, ast.Name) and func.id == "NotImplementedError"


def _merge_stub_file(py_path: Path, func_names: set[str]) -> bool:
    """Write or merge stubs into *py_path*. Returns True if file changed."""
    existing_funcs: dict[str, ast.FunctionDef] = {}
    if py_path.exists():
        text = py_path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for n in tree.body:
            if isinstance(n, ast.FunctionDef):
                existing_funcs[n.name] = n

    to_add: list[str] = []
    for name in sorted(func_names):
        if name in existing_funcs:
            if _is_stub_function(existing_funcs[name]):
                continue
            # Non-stub implementation — do not touch
            continue
        to_add.append(
            f"def {name}(*args, **kwargs):\n"
            f'    raise NotImplementedError("{STUB_MSG}")\n\n'
        )

    if not to_add:
        return False

    if not py_path.exists():
        py_path.parent.mkdir(parents=True, exist_ok=True)
        header = '"""Auto-generated SUT stubs — implement in agent-2-codegen."""\n\n'
        py_path.write_text(header + "".join(to_add), encoding="utf-8")
        return True

    out = py_path.read_text(encoding="utf-8")
    if not out.endswith("\n"):
        out += "\n"
    out += "\n# --- SUT stubs (auto-generated) ---\n" + "".join(to_add)
    py_path.write_text(out, encoding="utf-8")
    return True


def generate_stubs(*, tests_root: Path, app_root: Path) -> int:
    per_suffix = collect_required_stubs(tests_root)
    changed = 0
    for suffix in sorted(per_suffix):
        py_path = module_suffix_to_path(app_root, suffix)
        _ensure_pkg_inits(app_root, py_path)
        names = per_suffix[suffix]
        if _merge_stub_file(py_path, names):
            changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root (default: .)",
    )
    p.add_argument(
        "--tests-root",
        type=Path,
        default=None,
        help="Root of backend tests (default: <repo-root>/tests/backend)",
    )
    p.add_argument(
        "--app-root",
        type=Path,
        default=None,
        help="app package root (default: <repo-root>/src/backend/app)",
    )
    args = p.parse_args(argv)

    repo_root = args.repo_root.resolve()
    tests_root = (args.tests_root or repo_root / "tests" / "backend").resolve()
    app_root = (args.app_root or repo_root / "src" / "backend" / "app").resolve()

    if not tests_root.is_dir():
        print(f"generate_sut_stubs: no tests root {tests_root} — nothing to do", file=sys.stderr)
        return 0

    try:
        n = generate_stubs(tests_root=tests_root, app_root=app_root)
    except StubGenError as e:
        print(f"generate_sut_stubs: error: {e}", file=sys.stderr)
        return 1
    except (SyntaxError, OSError) as e:
        print(f"generate_sut_stubs: {e}", file=sys.stderr)
        return 1

    print(f"generate_sut_stubs: updated {n} module file(s) under {app_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
