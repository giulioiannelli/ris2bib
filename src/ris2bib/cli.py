"""
Command-line interface for converting RIS to BibTeX.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from .core import convert_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert RIS to BibTeX with lowercase keys.")
    parser.add_argument("inputs", nargs="+", help="Input .ris files")
    parser.add_argument("-o", "--output", help="Output .bib file (default: stdout)")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    def warn(message: str) -> None:
        sys.stderr.write(f"[warn] {message}\n")

    try:
        result = convert_files(args.inputs, output=args.output, on_warning=warn)
    except ValueError as exc:
        sys.stderr.write(f"[error] {exc}\n")
        return 1

    if args.output:
        sys.stdout.write(f"[info] Wrote {args.output}\n")
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
