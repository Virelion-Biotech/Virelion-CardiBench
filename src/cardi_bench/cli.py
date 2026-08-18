"""Command-line interface for CardiBench integrity checks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .manifest import assert_valid_manifest


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(prog="cardibench")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-manifest", help="validate a JSON benchmark manifest")
    validate.add_argument("path", type=Path)

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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
