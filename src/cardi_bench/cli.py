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


def _validate_manifest(path: Path) -> bool:
    try:
        assert_valid_manifest(_load_json(path))
    except (SystemExit, ValueError) as exc:
        print(f"INVALID: {path}: {exc}")
        return False
    print(f"valid: {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(prog="cardibench")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-manifest", help="validate one JSON benchmark manifest")
    validate.add_argument("path", type=Path)

    validate_all = sub.add_parser("validate-all-manifests", help="validate every JSON benchmark manifest")
    validate_all.add_argument("root", nargs="?", type=Path, default=Path("benchmarks/manifests"))

    catalog = sub.add_parser("list-benchmarks", help="list registered benchmark families")
    catalog.add_argument("--json", action="store_true", dest="as_json")

    audit = sub.add_parser("audit", help="audit repository structure")
    audit.add_argument("root", nargs="?", type=Path, default=Path("."))
    audit.add_argument("--strict", action="store_true", help="treat audit warnings as failures")

    args = parser.parse_args()
    if args.command == "validate-manifest":
        return 0 if _validate_manifest(args.path) else 1

    if args.command == "validate-all-manifests":
        paths = sorted(args.root.glob("*.json"))
        if not paths:
            print(f"No JSON manifests found under {args.root}")
            return 1
        results = [_validate_manifest(path) for path in paths]
        return 0 if all(results) else 1

    if args.command == "list-benchmarks":
        rows = [
            {"id": family.benchmark_id, "task": family.task, "group": family.preferred_group_key, "metrics": list(family.primary_metrics)}
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
        passed = result.passed and (not args.strict or not result.warnings)
        print("AUDIT PASS" if passed else "AUDIT FAIL")
        return 0 if passed else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
