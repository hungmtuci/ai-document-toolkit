#!/usr/bin/env python3
"""
convert_to_markdown.py — AI Document Toolkit v1.1.0
Convert any supported document to Markdown using MarkItDown & PyMuPDF4LLM.

Usage:
    python3 convert_to_markdown.py <file1> [file2] ...
"""

import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (
    TOOLKIT_VERSION, 
    PYMUPDF_FORMATS, 
    MARKITDOWN_FORMATS, 
    LIBREOFFICE_FORMATS,
    ALL_SUPPORTED_FORMATS
)
from common import (
    notify,
    safe_stem,
    now_log,
    convert_to_pdf_via_libreoffice,
)

def pymupdf_convert(input_path: Path) -> str:
    import pymupdf4llm
    return pymupdf4llm.to_markdown(str(input_path))

def markitdown_convert(input_path: Path) -> str:
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(input_path))
    return result.text_content

def process_file(file_arg: str) -> bool:
    path = Path(file_arg)

    if not path.exists():
        print(f"[ERROR] File not found: {file_arg}", file=sys.stderr)
        notify("Convert to Markdown Failed", f"File not found: {path.name}")
        return False

    ext = path.suffix.lower()

    if ext == ".txt":
        stem = safe_stem(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        md_path = path.parent / f"{stem}.md"
        md_path.write_text(f"# {stem}\n\n{text}", encoding="utf-8")
        notify("Markdown Created ✓", f"{path.name} → {md_path.name}")
        print(f"✓ Markdown created: {md_path}", file=sys.stderr)
        return True

    if ext not in ALL_SUPPORTED_FORMATS:
        print(f"[ERROR] Unsupported format '{ext}': {path.name}", file=sys.stderr)
        notify("Unsupported Format", f"{path.name} — '{ext}' is not supported.")
        return False

    notify("Converting to Markdown…", f"Processing {path.name}")
    print(f"[{now_log()}] Convert to Markdown: {path.name}", file=sys.stderr)

    stem = safe_stem(path)
    md_path = path.parent / f"{stem}.md"

    try:
        if ext in LIBREOFFICE_FORMATS:
            # Pre-convert legacy formats to PDF, then run PyMuPDF4LLM
            with tempfile.TemporaryDirectory(prefix="ai_toolkit_") as tmp:
                tmp_dir = Path(tmp)
                pdf_path = convert_to_pdf_via_libreoffice(path, tmp_dir)
                md_text = pymupdf_convert(pdf_path)
        elif ext in PYMUPDF_FORMATS:
            md_text = pymupdf_convert(path)
        elif ext in MARKITDOWN_FORMATS:
            md_text = markitdown_convert(path)
        else:
            raise ValueError(f"Unknown routing for {ext}")

        if not md_text.lstrip().startswith("#"):
            md_text = f"# {stem}\n\n{md_text}"

        md_path.write_text(md_text, encoding="utf-8")
        notify("Markdown Created ✓", f"{path.name} → {md_path.name}")
        print(f"✓ Markdown created: {md_path}", file=sys.stderr)
        return True

    except Exception as exc:
        notify("Conversion Failed ✗", f"{path.name} — {exc}")
        print(f"[ERROR] {exc}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print(
            f"Usage: convert_to_markdown.py <file> [file2] ...\n"
            f"Supported: {', '.join(sorted(ALL_SUPPORTED_FORMATS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    results = [process_file(f) for f in sys.argv[1:]]
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
