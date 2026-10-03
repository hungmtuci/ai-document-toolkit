#!/usr/bin/env python3
"""
convert_to_pdf.py — AI Document Toolkit v1.0.0
Convert any supported document to PDF using LibreOffice.

Usage:
    python3 convert_to_pdf.py <file1> [file2] ...
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from config import TOOLKIT_VERSION
from common import notify, find_soffice, safe_stem, now_log, convert_to_pdf_via_libreoffice

SUPPORTED_FORMATS = {
    ".doc", ".docx", ".rtf", ".odt",
    ".ppt", ".pptx", ".odp",
    ".xls", ".xlsx", ".ods", ".csv",
    ".html", ".htm", ".txt",
}


def process_file(file_arg: str) -> bool:
    path = Path(file_arg)

    if not path.exists():
        print(f"[ERROR] File not found: {file_arg}", file=sys.stderr)
        notify("Convert to PDF Failed", f"File not found: {path.name}")
        return False

    ext = path.suffix.lower()
    if ext == ".pdf":
        print(f"[INFO] Already a PDF: {path.name}", file=sys.stderr)
        notify("Already PDF", f"{path.name} is already a PDF.")
        return True

    if ext not in SUPPORTED_FORMATS:
        print(f"[ERROR] Unsupported format '{ext}': {path.name}", file=sys.stderr)
        notify("Unsupported Format", f"{path.name} — '{ext}' is not supported.")
        return False

    soffice = find_soffice()
    if not soffice:
        print("[ERROR] LibreOffice not found.", file=sys.stderr)
        notify("LibreOffice Required", "Install LibreOffice to convert this file.")
        return False

    output_dir = path.parent
    notify("Converting to PDF…", f"Processing {path.name}")
    print(f"[{now_log()}] Convert to PDF: {path.name}", file=sys.stderr)

    try:
        pdf_path = convert_to_pdf_via_libreoffice(path, output_dir)
        notify("PDF Created ✓", f"{path.name} → {pdf_path.name}")
        print(f"✓ PDF created: {pdf_path}", file=sys.stderr)
        return True
    except Exception as exc:
        notify("Conversion Failed ✗", f"{path.name} — {exc}")
        print(f"[ERROR] {exc}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print(
            f"Usage: convert_to_pdf.py <file> [file2] ...\n"
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    results = [process_file(f) for f in sys.argv[1:]]
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
