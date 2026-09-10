"""Core conversion logic: bulk PDF -> Markdown."""
from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Callable, Iterable

import pymupdf4llm


@dataclasses.dataclass
class ConversionResult:
    source: Path
    output: Path | None
    ok: bool
    error: str = ""
    deleted_source: bool = False
    delete_error: str = ""


def find_pdfs(root: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(p for p in root.glob(pattern) if p.is_file())


def convert_pdf(
    pdf_path: Path,
    source_root: Path,
    output_root: Path,
    preserve_structure: bool,
    delete_source: bool = False,
) -> ConversionResult:
    try:
        if preserve_structure:
            rel_dir = pdf_path.parent.relative_to(source_root)
        else:
            rel_dir = Path(".")
        target_dir = output_root / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        out_path = target_dir / (pdf_path.stem + ".md")
        out_path.write_text(md_text, encoding="utf-8")
        result = ConversionResult(source=pdf_path, output=out_path, ok=True)
    except Exception as exc:  # noqa: BLE001 - report per-file, keep batch going
        return ConversionResult(source=pdf_path, output=None, ok=False, error=str(exc))

    if delete_source:
        try:
            pdf_path.unlink()
            result.deleted_source = True
        except OSError as exc:
            result.delete_error = str(exc)

    return result


def convert_folder(
    source_folder: str | Path,
    output_subfolder_name: str = "markdown",
    recursive: bool = True,
    preserve_structure: bool = True,
    delete_source: bool = False,
    progress_callback: Callable[[int, int, ConversionResult], None] | None = None,
) -> tuple[Path, list[ConversionResult]]:
    """Convert every PDF under source_folder to a .md file under a new subfolder.

    If delete_source is True, each PDF is removed after its .md file is
    written successfully (a PDF that fails to convert is left in place).

    Returns (output_root, results).
    """
    source_root = Path(source_folder).expanduser().resolve()
    if not source_root.is_dir():
        raise NotADirectoryError(f"Not a folder: {source_root}")

    output_root = source_root / output_subfolder_name
    output_root.mkdir(parents=True, exist_ok=True)

    pdfs = [p for p in find_pdfs(source_root, recursive) if output_root not in p.parents]

    results: list[ConversionResult] = []
    total = len(pdfs)
    for i, pdf_path in enumerate(pdfs, start=1):
        result = convert_pdf(pdf_path, source_root, output_root, preserve_structure, delete_source)
        results.append(result)
        if progress_callback:
            progress_callback(i, total, result)

    return output_root, results
