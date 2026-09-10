"""Command-line entry point for bulk PDF -> Markdown conversion.

Usage:
    python cli.py /path/to/folder [--output-name markdown] [--no-recursive] [--flatten]
"""
from __future__ import annotations

import argparse
import sys

from pdf_to_md import convert_folder


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert all PDFs in a folder to Markdown.")
    parser.add_argument("folder", help="Folder containing PDF files")
    parser.add_argument(
        "--output-name", default="markdown", help="Name of the output subfolder (default: markdown)"
    )
    parser.add_argument(
        "--no-recursive", action="store_true", help="Only convert PDFs in the top-level folder"
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="Put all .md files directly in the output folder instead of mirroring subfolders",
    )
    args = parser.parse_args()

    def on_progress(done, total, result):
        status = "OK" if result.ok else f"FAIL ({result.error})"
        print(f"[{done}/{total}] {result.source.name}: {status}")

    output_root, results = convert_folder(
        args.folder,
        output_subfolder_name=args.output_name,
        recursive=not args.no_recursive,
        preserve_structure=not args.flatten,
        progress_callback=on_progress,
    )

    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    print(f"\nDone: {ok_count} converted, {fail_count} failed.")
    print(f"Output folder: {output_root}")
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
