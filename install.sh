#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  AI Document Toolkit — Installer (Alfred Edition)
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()     { error "$*"; exit 1; }

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  AI Document Toolkit — Alfred Installer${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# ── Step 1: Check Python 3 & Setup Virtual Env ─────────────────────────
echo -e "${BOLD}Step 1: Setting up Python Environment${RESET}"

is_py310_or_higher() {
    "$1" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null
}

PYTHON=""
# Search for Python >= 3.10 (required by MarkItDown)
candidates=(
    "$(command -v python3 2>/dev/null || true)"
    "$(command -v python3.12 2>/dev/null || true)"
    "$(command -v python3.11 2>/dev/null || true)"
    "$(command -v python3.10 2>/dev/null || true)"
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "$HOME/miniconda3/bin/python3"
    "$HOME/anaconda3/bin/python3"
    "$HOME/miniforge3/bin/python3"
)

for c in "${candidates[@]}"; do
    if [ -n "$c" ] && [ -x "$c" ]; then
        if is_py310_or_higher "$c"; then
            PYTHON="$c"
            break
        fi
    fi
done

[ -z "$PYTHON" ] && die "Python >= 3.10 is required by MarkItDown. Please install Python 3.10+ via Homebrew or Conda."

PY_VER=$("$PYTHON" --version 2>&1)
success "Base Python: $PYTHON ($PY_VER)"

VENV_DIR="$PROJECT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"

# If .venv exists but is using Python < 3.10, auto-recreate it!
if [ -d "$VENV_DIR" ] && [ -x "$VENV_PYTHON" ]; then
    if ! is_py310_or_higher "$VENV_PYTHON"; then
        warn "Existing .venv is using Python < 3.10 (incompatible with MarkItDown). Recreating .venv..."
        rm -rf "$VENV_DIR"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at .venv..."
    "$PYTHON" -m venv "$VENV_DIR" || die "Failed to create virtual environment."
fi

VENV_PYTHON="$VENV_DIR/bin/python3"
success "Active Python: $VENV_PYTHON"


# ── Step 2: Check LibreOffice ─────────────────────────────────────────
echo ""
echo -e "${BOLD}Step 2: Checking LibreOffice${RESET}"
SOFFICE=""
for c in \
    "/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    "/usr/local/bin/soffice" "/opt/homebrew/bin/soffice"; do
    if [ -f "$c" ] && [ -x "$c" ]; then SOFFICE="$c"; break; fi
done
command -v soffice &>/dev/null && [ -z "$SOFFICE" ] && SOFFICE="$(command -v soffice)"
if [ -z "$SOFFICE" ]; then
    warn "LibreOffice not found. DOC/XLS/PPT conversion will be limited."
else
    success "LibreOffice: $SOFFICE"
fi

# ── Step 3: Install Dependencies ────────────────────────────
echo ""
echo -e "${BOLD}Step 3: Checking AI Dependencies in Virtual Environment${RESET}"

if "$VENV_PYTHON" -c "from markitdown import MarkItDown; import pymupdf4llm" &>/dev/null; then
    success "Dependencies (markitdown, pymupdf4llm) are already installed."
else
    warn "Dependencies missing in .venv. Installing (this may take a minute)..."
    "$VENV_PYTHON" -m pip install --upgrade pip --quiet
    "$VENV_PYTHON" -m pip install "markitdown[all]" pymupdf4llm --quiet || die "Failed to install dependencies."
    success "Dependencies installed."
fi

# ── Step 4: Build Alfred Workflow ─────────────────────────────────────
echo ""
echo -e "${BOLD}Step 4: Building Alfred Workflow${RESET}"

"$VENV_PYTHON" "$SCRIPTS_DIR/build_alfred.py" "$PROJECT_DIR" || die "Failed to build Alfred Workflow."

WORKFLOW_FILE="$PROJECT_DIR/AI Toolkit.alfredworkflow"

if [ -f "$WORKFLOW_FILE" ]; then
    success "Workflow built successfully."
    echo ""
    echo -e "${BOLD}Step 5: Installing into Alfred${RESET}"
    open "$WORKFLOW_FILE"
    info "Alfred should now open and prompt you to import the 'AI Toolkit' workflow."
else
    die "Workflow file was not created."
fi

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✓ Installation Complete!${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${BOLD}How to use:${RESET}"
echo -e "  1. Select a file (or multiple files) in Finder."
echo -e "  2. Open Alfred (e.g., Option + Space)."
echo -e "  3. Type ${BOLD}ai${RESET} and select the desired conversion action."
echo ""
