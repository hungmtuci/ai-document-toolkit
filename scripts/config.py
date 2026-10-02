"""
config.py — Central configuration for AI Document Toolkit
"""

import os

# ─── Toolkit Version ──────────────────────────────────────────────────────────
TOOLKIT_VERSION = "1.0.0"

# ─── LibreOffice Binary ───────────────────────────────────────────────────────
SOFFICE_CANDIDATES = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/local/bin/soffice",
    "/opt/homebrew/bin/soffice",
    "soffice",  # fallback: in PATH
]

# ─── Format Routing ───────────────────────────────────────────────────────────
# Formats PyMuPDF4LLM handles (PDFs)
PYMUPDF_FORMATS = {
    ".pdf",
}

# Formats MarkItDown handles natively
MARKITDOWN_FORMATS = {
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".md",
}

# Formats that need LibreOffice → DOCX/PDF pre-conversion
LIBREOFFICE_FORMATS = {
    ".doc",
    ".rtf",
    ".xls",
    ".ppt",
    ".odt",
    ".ods",
    ".odp",
}

# Plain text — read directly
PLAIN_TEXT_FORMATS = {
    ".txt",
}

# All supported formats
ALL_SUPPORTED_FORMATS = (
    PYMUPDF_FORMATS
    | MARKITDOWN_FORMATS
    | LIBREOFFICE_FORMATS
    | PLAIN_TEXT_FORMATS
)

# ─── Output Settings ──────────────────────────────────────────────────────────
# Suffix appended to the source filename stem for the AI package folder
AI_PACKAGE_SUFFIX = "_AI"

# ─── Notification Settings ────────────────────────────────────────────────────
NOTIFY_APP = "AI Document Toolkit"
