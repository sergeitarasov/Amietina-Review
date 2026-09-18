#!/usr/bin/env python3
"""Remove PhenoScript's generated metadata header from Markdown files."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path


DEFAULT_DIRECTORY = Path("Amietina_phenoscript/output/nl")
METADATA_MARKERS = (
    "Catalog Number",
    "has role in modeling",
    "Parent Name Usage ID",
    "Taxon ID",
)


def markdown_files(paths: list[Path]) -> list[Path]:
    """Return unique Markdown files from the supplied files and directories."""
    found: set[Path] = set()
    for path in paths:
        if path.is_dir():
            found.update(item for item in path.rglob("*.md") if item.is_file())
        elif path.is_file() and path.suffix.lower() == ".md":
            found.add(path)
        else:
            print(f"warning: skipping missing or non-Markdown path: {path}", file=sys.stderr)
    return sorted(found)


def cleaned_text(text: str) -> tuple[str, bool]:
    """Remove a recognized initial metadata block and its separator."""
    lines = text.splitlines(keepends=True)
    separator = next(
        (index for index, line in enumerate(lines) if line.strip() == "---"), None
    )
    if separator is None:
        return text, False

    header = "".join(lines[:separator])
    if not any(marker in header for marker in METADATA_MARKERS):
        return text, False

    first_content_line = separator + 1
    while first_content_line < len(lines) and not lines[first_content_line].strip():
        first_content_line += 1
    return "".join(lines[first_content_line:]), True


def atomic_write(path: Path, text: str) -> None:
    """Replace a file without exposing a partially written result."""
    stat = path.stat()
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as temporary:
        temporary.write(text)
        temporary_path = Path(temporary.name)
    os.chmod(temporary_path, stat.st_mode)
    os.replace(temporary_path, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove the PhenoScript metadata block before the first Markdown "
            "'---' separator. Safe to run repeatedly."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[DEFAULT_DIRECTORY],
        help=f"Markdown files or directories (default: {DEFAULT_DIRECTORY})",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run", action="store_true", help="report files without changing them"
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="make no changes and exit 1 if any file still contains the header",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = markdown_files(args.paths)
    changed = 0

    for path in files:
        original = path.read_text(encoding="utf-8")
        cleaned, needs_change = cleaned_text(original)
        if not needs_change:
            continue
        changed += 1
        action = "would clean" if args.dry_run or args.check else "cleaned"
        print(f"{action}: {path}")
        if not args.dry_run and not args.check:
            atomic_write(path, cleaned)

    if changed == 0:
        print(f"No PhenoScript metadata headers found in {len(files)} Markdown file(s).")
    elif args.dry_run:
        print(f"Would clean {changed} of {len(files)} Markdown file(s).")
    elif not args.check:
        print(f"Cleaned {changed} of {len(files)} Markdown file(s).")

    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
