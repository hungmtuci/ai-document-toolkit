#!/usr/bin/env python3
"""
convert_for_ai.py — AI Document Toolkit v1.1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Converts any supported document into a complete AI-ready package using ultra-fast AI optimized engines (MarkItDown, PyMuPDF4LLM).

Usage:
    python3 convert_for_ai.py <file1> [file2] ...
"""

import sys
import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

_SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (
    TOOLKIT_VERSION, 
    PYMUPDF_FORMATS,
    MARKITDOWN_FORMATS,
    LIBREOFFICE_FORMATS,
    PLAIN_TEXT_FORMATS,
    ALL_SUPPORTED_FORMATS,
    AI_PACKAGE_SUFFIX
)
from common import (
    notify,
    safe_stem,
    now_log,
    convert_to_pdf_via_libreoffice,
    ConversionLogger
)

class AIPackageBuilder:
    def __init__(self, source_path: Path):
        self.source = source_path
        self.stem = safe_stem(self.source)
        self.ext = self.source.suffix.lower()

        self.pkg_dir = self.source.parent / f"{self.stem}{AI_PACKAGE_SUFFIX}"
        self.logs_dir = self.pkg_dir / "logs"

        self.status = "pending"
        self.errors = []
        self.output_files = []
        self.log = None

    def build(self) -> bool:
        try:
            self.pkg_dir.mkdir(parents=True, exist_ok=True)
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self.log = ConversionLogger(self.logs_dir / "convert.log", echo=True)
            self.log.section("Source File")
            self.log.info(f"Path   : {self.source}")
            self.log.info(f"Format : {self.ext}")

            if self.ext in PLAIN_TEXT_FORMATS:
                self._process_plain_text()
            elif self.ext in PYMUPDF_FORMATS:
                self._process_with_pymupdf(self.source)
            elif self.ext in MARKITDOWN_FORMATS:
                self._process_with_markitdown(self.source)
            elif self.ext in LIBREOFFICE_FORMATS:
                self._process_via_libreoffice()
            else:
                raise ValueError(f"Unsupported format '{self.ext}'.")

            self._write_readme()
            self._write_manifest(status="success")
            self.status = "success"
            self.log.section("Finished")
            self.log.info("Conversion completed successfully.")
            return True

        except Exception as exc:
            self.errors.append(str(exc))
            self.status = "error"
            if self.log:
                self.log.error(str(exc))
            else:
                print(f"[ERROR] {exc}", file=sys.stderr)
            try:
                self._write_manifest(status="error")
            except Exception:
                pass
            return False
        finally:
            if self.log:
                self.log.close(self.status)

    def _process_plain_text(self):
        self.log.section("Processing Plain Text")
        text = self.source.read_text(encoding="utf-8", errors="replace")
        self._write_outputs(text)

    def _process_via_libreoffice(self):
        self.log.section("LibreOffice Pre-conversion")
        with tempfile.TemporaryDirectory(prefix="ai_toolkit_") as tmp:
            tmp_dir = Path(tmp)
            self.log.info(f"Temp dir: {tmp_dir}")
            pdf_path = convert_to_pdf_via_libreoffice(self.source, tmp_dir, logger=self.log)
            self._process_with_pymupdf(pdf_path)
        self.log.info("Temporary PDF cleaned up.")

    def _process_with_pymupdf(self, input_path: Path):
        self.log.section("PyMuPDF4LLM Conversion")
        self.log.info(f"Input: {input_path}")
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(str(input_path))
        self._write_outputs(md_text)

    def _process_with_markitdown(self, input_path: Path):
        self.log.section("MarkItDown Conversion")
        self.log.info(f"Input: {input_path}")
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(str(input_path))
        self._write_outputs(result.text_content)

    def _write_outputs(self, text_content: str):
        if not text_content.lstrip().startswith("#"):
            text_content = f"# {self.stem}\n\n{text_content}"
            
        md_path = self.pkg_dir / f"{self.stem}.md"
        txt_path = self.pkg_dir / f"{self.stem}.txt"
        html_path = self.pkg_dir / f"{self.stem}.html"
        json_path = self.pkg_dir / f"{self.stem}.json"
        
        md_path.write_text(text_content, encoding="utf-8")
        self.output_files.append(md_path.name)
        
        txt_path.write_text(text_content, encoding="utf-8")
        self.output_files.append(txt_path.name)
        
        html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{self.stem}</title></head><body><pre>{text_content}</pre></body></html>"
        html_path.write_text(html_content, encoding="utf-8")
        self.output_files.append(html_path.name)
        
        doc_json = {
            "source": self.source.name,
            "format": "md",
            "content": text_content,
            "metadata": {"title": self.stem},
        }
        json_path.write_text(json.dumps(doc_json, ensure_ascii=False, indent=2), encoding="utf-8")
        self.output_files.append(json_path.name)

    def _write_readme(self):
        readme_path = self.pkg_dir / "README.md"
        lines = [
            f"# AI Package: {self.stem}",
            "",
            "## Source Document",
            f"- **Filename:** `{self.source.name}`",
            f"- **Format:** `{self.ext}`",
            f"- **Generated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            f"- **Toolkit Version:** `{TOOLKIT_VERSION}`",
            "",
            "## Contents",
            "- `*.md`: Optimized Markdown for LLM reading (Primary)",
            "- `*.txt`: Plain text fallback",
            "- `*.json`: Structured payload for API ingestion",
            "- `logs/`: Conversion logs and errors",
            "",
            "## Status",
            f"**{self.status.upper()}**",
        ]
        if self.errors:
            lines.append("")
            lines.append("### Errors Encountered")
            for err in self.errors:
                lines.append(f"- {err}")

        readme_path.write_text("\n".join(lines), encoding="utf-8")
        self.output_files.append(readme_path.name)
        self.log.info("Generated README.md")

    def _write_manifest(self, status: str):
        manifest_path = self.pkg_dir / "manifest.json"
        manifest_data = {
            "source_file": self.source.name,
            "original_format": self.ext,
            "generated_at": datetime.now().isoformat(),
            "toolkit_version": TOOLKIT_VERSION,
            "status": status,
            "errors": self.errors,
            "files": self.output_files,
        }
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        self.log.info("Generated manifest.json")


def process_file(file_arg: str) -> bool:
    path = Path(file_arg)

    if not path.exists():
        print(f"[ERROR] File not found: {file_arg}", file=sys.stderr)
        notify("Conversion Failed", f"File not found: {path.name}")
        return False

    if path.suffix.lower() not in ALL_SUPPORTED_FORMATS:
        print(f"[ERROR] Unsupported format '{path.suffix}': {path.name}", file=sys.stderr)
        notify("Unsupported Format", f"{path.name} — '{path.suffix}' is not supported.")
        return False

    notify("Converting for AI…", f"Processing {path.name}")
    print(f"[{now_log()}] AI Convert: {path.name}", file=sys.stderr)

    builder = AIPackageBuilder(path)
    success = builder.build()

    if success:
        notify("AI Package Ready ✓", f"Created {builder.pkg_dir.name}/")
        print(f"✓ AI Package generated: {builder.pkg_dir}", file=sys.stderr)
        return True
    else:
        notify("Conversion Failed ✗", f"{path.name} — Check logs.")
        return False


def main():
    if len(sys.argv) < 2:
        print(
            f"Usage: convert_for_ai.py <file> [file2] ...\n"
            f"Supported: {', '.join(sorted(ALL_SUPPORTED_FORMATS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    results = [process_file(f) for f in sys.argv[1:]]
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
