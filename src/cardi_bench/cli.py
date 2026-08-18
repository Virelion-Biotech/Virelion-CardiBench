"""Command-line interface for CardiBench integrity and release checks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import BENCHMARK_FAMILIES
from .manifest import assert_valid_manifest
from .release import audit_repository_paths


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(prog="cardibench")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-manifest", help="validate one JSON benchmark manifest")
    validate.add_argument("path", type=Path)

    catalog = sub.add_parser("list-benchmarks", help="list registered benchmark families")
    catalog.add_argument("--json", action="store_true", dest="as_json")

    audit = sub.add_parser("audit", help="audit repository structure")
    audit.add_argument("root", nargs="?", type=Path, default=Path("."))

    args = parser.parse_args()
    if args.command == "validate-manifest":
        manifest = _load_json(args.path)
        try:
            assert_valid_manifest(manifest)
        except ValueError as exc:
            print(exc)
            return 1
        print(f"valid: {args.path}")
        return 0

    if args.command == "list-benchmarks":
        rows = [
            {
                "id": family.benchmark_id,
                "task": family.task,
                "group": family.preferred_group_key,
                "metrics": list(family.primary_metrics),
            }
            for family in BENCHMARK_FAMILIES
        ]
        if args.as_json:
            print(json.dumps(rows, indent=2))
        else:
            for row in rows:
                print(f"{row['id']}: {row['task']} [{row['group']}]")
        return 0

    if args.command == "audit":
        paths = [str(p.relative_to(args.root)) for p in args.root.rglob("*") if p.is_file()]
        result = audit_repository_paths(paths)
        for error in result.errors:
            print(f"ERROR: {error}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        print("AUDIT PASS" if result.passed else "AUDIT FAIL")
        return 0 if result.passed else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
