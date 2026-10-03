#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  AI Document Toolkit — Uninstaller (Alfred Edition)
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  AI Document Toolkit — Uninstaller${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════${RESET}"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Clean up generated workflow files
WORKFLOW_FILE="$PROJECT_DIR/AI Toolkit.alfredworkflow"
if [ -f "$WORKFLOW_FILE" ]; then
    rm "$WORKFLOW_FILE"
    success "Removed generated $WORKFLOW_FILE"
fi

# Clean up legacy Automator services if they exist
SERVICES_DIR="$HOME/Library/Services"
for name in "Convert to PDF" "Convert to Markdown" "Convert for AI"; do
    if [ -d "$SERVICES_DIR/$name.workflow" ]; then
        rm -rf "$SERVICES_DIR/$name.workflow"
        success "Removed legacy service: $name.workflow"
    fi
done

# Restart pbs if we removed services
/System/Library/CoreServices/pbs -update 2>/dev/null || true
killall pbs 2>/dev/null || true

echo ""
echo -e "${BOLD}To complete the uninstallation from Alfred:${RESET}"
echo -e "  1. Open Alfred Preferences (Option + Space, type 'Alfred', press Cmd+,)"
echo -e "  2. Go to the ${BOLD}Workflows${RESET} tab"
echo -e "  3. Find ${BOLD}AI Toolkit${RESET} in the sidebar"
echo -e "  4. Right-click it and select ${BOLD}Delete${RESET}"
echo ""
success "Local cleanup complete."
