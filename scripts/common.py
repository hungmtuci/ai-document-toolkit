from __future__ import annotations

import os
import sys
import subprocess
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import SOFFICE_CANDIDATES, NOTIFY_APP, TOOLKIT_VERSION


# ─── macOS Notifications ──────────────────────────────────────────────────────

def notify(title: str, message: str) -> None:
    """Send a macOS notification via osascript."""
    script = (
        f'display notification "{message}" '
        f'with title "{NOTIFY_APP}" '
        f'subtitle "{title}"'
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except Exception:
        pass  # Notification failure is non-fatal


# ─── LibreOffice Discovery ────────────────────────────────────────────────────

def find_soffice() -> Optional[str]:
    """Find the LibreOffice soffice binary. Returns path or None."""
    for candidate in SOFFICE_CANDIDATES:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        # Also try shutil.which for names in PATH
        found = shutil.which(candidate)
        if found:
            return found
    return None


# ─── Unicode-safe filename utilities ─────────────────────────────────────────

def safe_stem(path: Path) -> str:
    """
    Return the filename stem, NFC-normalised to handle Vietnamese and
    other Unicode filenames consistently across macOS (NFD) and other systems.
    """
    return unicodedata.normalize("NFC", path.stem)


# ─── Timestamp helpers ────────────────────────────────────────────────────────

def now_iso() -> str:
    """Return current local time as ISO 8601 string."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_log() -> str:
    """Return current local time as a human-readable log string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── Logging helper ───────────────────────────────────────────────────────────

class ConversionLogger:
    """Simple logger that writes to a file and optionally to stderr."""

    def __init__(self, log_path: Path, echo: bool = True):
        self.log_path = log_path
        self.echo = echo
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(log_path, "w", encoding="utf-8")
        self._write_header()

    def _write_header(self):
        self._write(f"AI Document Toolkit v{TOOLKIT_VERSION}")
        self._write(f"Log started: {now_log()}")
        self._write("-" * 60)

    def _write(self, line: str):
        self._file.write(line + "\n")
        self._file.flush()
        if self.echo:
            print(line, file=sys.stderr)

    def info(self, msg: str):
        self._write(f"[INFO]  {now_log()} — {msg}")

    def warn(self, msg: str):
        self._write(f"[WARN]  {now_log()} — {msg}")

    def error(self, msg: str):
        self._write(f"[ERROR] {now_log()} — {msg}")

    def section(self, title: str):
        self._write("")
        self._write(f"{'─' * 60}")
        self._write(f"  {title}")
        self._write(f"{'─' * 60}")

    def close(self, status: str = "OK"):
        self._write("")
        self._write("-" * 60)
        self._write(f"Log finished: {now_log()}")
        self._write(f"Status: {status}")
        self._file.close()


# ─── LibreOffice PDF conversion ───────────────────────────────────────────────

def convert_to_pdf_via_libreoffice(
    input_path: Path,
    output_dir: Path,
    logger: Optional[ConversionLogger] = None,
) -> Path:
    """
    Convert input_path to PDF using LibreOffice and save it in output_dir.
    Returns the path of the generated PDF.
    Raises RuntimeError on failure.
    """
    soffice = find_soffice()
    if not soffice:
        raise RuntimeError(
            "LibreOffice not found. Install LibreOffice to convert this file type."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(input_path),
    ]

    if logger:
        logger.info(f"LibreOffice: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"LibreOffice conversion failed: {msg}")

    # LibreOffice names the output file as <stem>.pdf in output_dir
    pdf_path = output_dir / (input_path.stem + ".pdf")
    if not pdf_path.exists():
        # Search for any pdf produced
        pdfs = list(output_dir.glob("*.pdf"))
        if pdfs:
            pdf_path = pdfs[0]
        else:
            raise RuntimeError(
                f"LibreOffice ran successfully but produced no PDF in {output_dir}"
            )

    if logger:
        logger.info(f"LibreOffice produced: {pdf_path.name}")

    return pdf_path


# ─── Docling version ──────────────────────────────────────────────────────────

def get_docling_version() -> str:
    """Return installed Docling version, or 'unknown'."""
    try:
        import importlib.metadata
        return importlib.metadata.version("docling")
    except Exception:
        return "unknown"
