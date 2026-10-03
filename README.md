# AI Document Toolkit

**One right-click. A complete AI-ready document package.**

---

## What It Does

Right-click any document in Finder → **Convert for AI** → an `_AI/` folder appears beside your document, containing everything needed to work with any LLM.

```
Research.docx
Research_AI/
├── Research.md       ← Markdown, optimised for LLM reading
├── Research.txt      ← Plain text, maximum compatibility
├── Research.html     ← HTML with structure preserved
├── Research.json     ← Full Docling document model (JSON)
├── README.md         ← Auto-generated package summary
├── manifest.json     ← Machine-readable manifest
├── logs/
│   └── convert.log   ← Full conversion log
├── images/           ← Extracted figures and images
└── tables/           ← Extracted tables as CSV
```

---

## Quick Actions

| Action | What it does |
|---|---|
| **Convert for AI** | Full AI package (MD + TXT + HTML + JSON + metadata) |
| **Convert to PDF** | Convert any document to PDF using LibreOffice |
| **Convert to Markdown** | Convert any document to Markdown using Docling |

---

## Supported Formats

| Format | Route |
|---|---|
| PDF | Docling direct |
| DOCX, PPTX, XLSX, ODT, ODP, ODS | Docling direct |
| HTML, CSV | Docling direct |
| DOC, RTF, XLS, PPT | LibreOffice → PDF → Docling |
| TXT | Read directly |

---

## Requirements

| Tool | Purpose | Install |
|---|---|---|
| Python 3.9+ | Core runtime | `brew install python3` |
| [Docling](https://github.com/DS4SD/docling) | Document intelligence | `pip3 install docling` |
| [LibreOffice](https://www.libreoffice.org/) | Legacy format conversion | [Download](https://www.libreoffice.org/download/) |

---

## Installation

```bash
git clone https://github.com/yourname/ai-document-toolkit
cd ai-document-toolkit
bash install.sh
```

The installer:
1. Checks Python, LibreOffice, and Docling
2. Installs any missing Python packages
3. Copies Quick Actions to `~/Library/Services/`
4. Reloads the macOS Services menu

---

## Usage

### Via Finder (recommended)

1. Right-click any document in Finder
2. Choose **Quick Actions** → **Convert for AI**
3. Wait for the notification: *"Conversion Complete ✓"*
4. Open the `<name>_AI/` folder beside your original file

### Via Command Line

```bash
# Convert for AI
python3 scripts/convert_for_ai.py path/to/document.docx

# Convert to PDF
python3 scripts/convert_to_pdf.py path/to/document.docx

# Convert to Markdown
python3 scripts/convert_to_markdown.py path/to/document.docx

# Multiple files at once
python3 scripts/convert_for_ai.py doc1.pdf doc2.docx doc3.xlsx
```

---

## AI Package Details

### README.md (auto-generated)
- Source filename, format, full path
- Conversion timestamp and toolkit version
- Docling version
- Package contents table
- Usage instructions per AI tool

### manifest.json (auto-generated)
```json
{
  "toolkit_version": "1.0.0",
  "docling_version": "2.107.0",
  "source": {
    "filename": "Research.docx",
    "format": ".docx"
  },
  "timestamps": {
    "start": "2026-06-27T17:00:00+07:00",
    "end": "2026-06-27T17:00:45+07:00"
  },
  "status": "success",
  "output_files": ["Research.md", "Research.txt", ...]
}
```

### logs/convert.log
```
AI Document Toolkit v1.0.0
Log started: 2026-06-27 17:00:00
────────────────────────────────────────────────────────────
[INFO]  2026-06-27 17:00:00 — Path   : /Users/.../Research.docx
[INFO]  2026-06-27 17:00:00 — Format : .docx
...
```

---

## Using With AI Tools

| Tool | Best file to upload |
|---|---|
| **ChatGPT** | `Research.md` or `Research.txt` |
| **Claude** | `Research.md` |
| **Gemini** | `Research.md` or `Research.txt` |
| **NotebookLM** | `Research.md` |
| **API / Programmatic** | `Research.json` |

---

## Troubleshooting

### "Convert for AI" doesn't appear in right-click menu

Go to **System Settings → Privacy & Security → Extensions → Finder Extensions** and enable the workflows.  
Or log out and back in.

### LibreOffice conversion fails

Make sure LibreOffice is installed at `/Applications/LibreOffice.app`.  
Download from [libreoffice.org](https://www.libreoffice.org/download/).

### Docling not found

```bash
pip3 install docling
```

### Permission denied

```bash
chmod +x install.sh uninstall.sh
bash install.sh
```

---

## Uninstall

```bash
bash uninstall.sh
```

---

## Project Structure

```
ai-document-toolkit/
├── scripts/
│   ├── config.py               ← Central constants
│   ├── common.py               ← Shared utilities
│   ├── convert_for_ai.py       ← Main AI package engine
│   ├── convert_to_pdf.py       ← PDF converter
│   └── convert_to_markdown.py  ← Markdown converter
├── automator/
│   ├── Convert for AI.workflow
│   ├── Convert to PDF.workflow
│   └── Convert to Markdown.workflow
├── install.sh                  ← One-command installer
├── uninstall.sh                ← One-command uninstaller
└── README.md
```

---

## Philosophy

> One click. One output. Zero manual cleanup.

Whenever a step can be automated safely, it is automated.  
The user should never need to choose the document type, create output folders, generate metadata, or clean up temporary files.

---

## License

MIT
