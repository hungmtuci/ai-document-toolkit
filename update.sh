#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  AI Document Toolkit — Updater
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()     { error "$*"; exit 1; }

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  AI Document Toolkit — Updater${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

info "Pulling latest changes from GitHub..."
git checkout -- . 2>/dev/null || true
if git pull origin main; then
    success "Successfully updated from GitHub."
else
    # Try just 'git pull' in case tracking branch is different
    if git pull; then
        success "Successfully updated from GitHub."
    else
        die "Failed to pull changes from GitHub."
    fi
fi

echo ""
info "Running installer to apply updates..."
if [ -x "./install.sh" ]; then
    ./install.sh
else
    bash ./install.sh
fi
