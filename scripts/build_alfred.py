#!/usr/bin/env python3
"""
build_alfred.py — Creates an Alfred Workflow for the AI Document Toolkit.

This generates a .alfredworkflow file (a zipped folder containing info.plist).
"""

import os
import sys
import plistlib
import zipfile
import json
from pathlib import Path

# UIDs
UID_INPUT_LIST = "7EE42DF9-0266-412C-A3BB-8239F3218DA4"
UID_SCRIPT_LIST = "2B81F275-8D63-4700-AA52-FFEF7A46AD98"
UID_NOTIFY = "B403B520-22D3-4CDA-B034-BA75B46D9E93"

# Universal Action UIDs
UID_UA_PDF = "UA-PDF-UID-0000-0000-000000000000"
UID_UA_MD  = "UA-MD-UID-0000-0000-000000000000"
UID_UA_AI  = "UA-AI-UID-0000-0000-000000000000"

UID_SCRIPT_PDF = "SCRIPT-PDF-UID-0000-0000-000000"
UID_SCRIPT_MD  = "SCRIPT-MD-UID-0000-0000-000000"
UID_SCRIPT_AI  = "SCRIPT-AI-UID-0000-0000-000000"

# Script for List Filter (Grabs Finder Selection)
def make_list_script(toolkit_dir: str) -> str:
    return f"""#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

ACTION="$1"
TOOLKIT_DIR="{toolkit_dir}"
PYTHON_BIN="/opt/homebrew/bin/python3"

if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="/usr/local/bin/python3"
fi
if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="/usr/bin/python3"
fi
if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="python3"
fi

FILES=$(osascript -e '
tell application "Finder"
    set theSelection to selection
    set fileList to ""
    repeat with i in theSelection
        set fileList to fileList & POSIX path of (i as alias) & "\\n"
    end repeat
    return fileList
end tell
')

if [ -z "$FILES" ]; then
    echo "No files selected in Finder."
    exit 0
fi

while IFS= read -r file; do
    if [ -n "$file" ]; then
        if [ "$ACTION" == "pdf" ]; then
            "$PYTHON_BIN" "$TOOLKIT_DIR/scripts/convert_to_pdf.py" "$file"
        elif [ "$ACTION" == "md" ]; then
            "$PYTHON_BIN" "$TOOLKIT_DIR/scripts/convert_to_markdown.py" "$file"
        elif [ "$ACTION" == "ai" ]; then
            "$PYTHON_BIN" "$TOOLKIT_DIR/scripts/convert_for_ai.py" "$file"
        fi
    fi
done <<< "$FILES"
echo "Action completed."
"""

# Script for Universal Actions (Receives files as args)
def make_ua_script(action: str, toolkit_dir: str) -> str:
    script_name = {
        "pdf": "convert_to_pdf.py",
        "md": "convert_to_markdown.py",
        "ai": "convert_for_ai.py"
    }[action]
    
    return f"""#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

TOOLKIT_DIR="{toolkit_dir}"
PYTHON_BIN="/opt/homebrew/bin/python3"

if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="/usr/local/bin/python3"
fi
if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="/usr/bin/python3"
fi
if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="python3"
fi

for file in "$@"; do
    if [ -n "$file" ]; then
        "$PYTHON_BIN" "$TOOLKIT_DIR/scripts/{script_name}" "$file"
    fi
done
echo "Action completed."
"""

def make_universal_action(name: str, uid: str) -> dict:
    return {
        "config": {
            "acceptsfiles": True,
            "acceptsmulti": 1,
            "acceptstext": False,
            "acceptsurls": False,
            "name": name
        },
        "type": "alfred.workflow.trigger.universalaction",
        "uid": uid,
        "version": 1
    }

def make_script_action(script: str, uid: str) -> dict:
    return {
        "config": {
            "concurrently": False,
            "escaping": 102,
            "script": script,
            "scriptargtype": 1, # with input as argv ($1, $2, ...)
            "scriptfile": "",
            "type": 0 # bash
        },
        "type": "alfred.workflow.action.script",
        "uid": uid,
        "version": 2
    }

def build_info_plist(toolkit_dir: str) -> dict:
    list_items = [
        {"title": "Convert to PDF", "arg": "pdf", "subtitle": "Convert selected document(s) to PDF format"},
        {"title": "Convert to Markdown", "arg": "md", "subtitle": "Convert selected document(s) to Markdown format"},
        {"title": "Convert for AI", "arg": "ai", "subtitle": "Process selected document(s) for AI context"}
    ]

    objects = [
        # List Filter
        {
            "config": {
                "argumenttrimmode": 0,
                "argumenttype": 1,
                "keyword": "ai",
                "runningsubtext": "",
                "subtext": "Convert Document with AI Toolkit",
                "title": "AI Toolkit",
                "withspace": True,
                "items": json.dumps(list_items)
            },
            "type": "alfred.workflow.input.listfilter",
            "uid": UID_INPUT_LIST,
            "version": 1
        },
        # Script for List Filter
        make_script_action(make_list_script(toolkit_dir), UID_SCRIPT_LIST),
        
        # Universal Actions
        make_universal_action("Convert to PDF", UID_UA_PDF),
        make_universal_action("Convert to Markdown", UID_UA_MD),
        make_universal_action("Convert for AI", UID_UA_AI),
        
        # Scripts for Universal Actions
        make_script_action(make_ua_script("pdf", toolkit_dir), UID_SCRIPT_PDF),
        make_script_action(make_ua_script("md", toolkit_dir), UID_SCRIPT_MD),
        make_script_action(make_ua_script("ai", toolkit_dir), UID_SCRIPT_AI),
        
        # Output Notification
        {
            "config": {
                "lastpathcomponent": False,
                "onlyshowifquerypopulated": False,
                "removeextension": False,
                "text": "{query}",
                "title": "AI Toolkit"
            },
            "type": "alfred.workflow.output.notification",
            "uid": UID_NOTIFY,
            "version": 1
        }
    ]

    connections = {
        UID_INPUT_LIST: [{"destinationuid": UID_SCRIPT_LIST, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_UA_PDF: [{"destinationuid": UID_SCRIPT_PDF, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_UA_MD: [{"destinationuid": UID_SCRIPT_MD, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_UA_AI: [{"destinationuid": UID_SCRIPT_AI, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        
        # All scripts route to the notification
        UID_SCRIPT_LIST: [{"destinationuid": UID_NOTIFY, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_SCRIPT_PDF: [{"destinationuid": UID_NOTIFY, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_SCRIPT_MD: [{"destinationuid": UID_NOTIFY, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
        UID_SCRIPT_AI: [{"destinationuid": UID_NOTIFY, "modifiers": 0, "modifiersubtext": "", "vitoclose": False}],
    }

    return {
        "bundleid": "com.hunglx.aitoolkit",
        "name": "AI Toolkit",
        "description": "Convert documents to PDF, Markdown, or process for AI.",
        "createdby": "AI Installer",
        "version": "1.0.1",
        "readme": "Select files in Finder, invoke Alfred, type 'ai', and choose your conversion action. Or use Universal Actions.",
        "objects": objects,
        "connections": connections
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: build_alfred.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_path = output_dir / "AI Toolkit.alfredworkflow"
    
    # We use the absolute path to output_dir as the toolkit_dir.
    toolkit_dir = str(output_dir.resolve())
    plist_data = build_info_plist(toolkit_dir)

    with zipfile.ZipFile(workflow_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        plist_bytes = plistlib.dumps(plist_data, fmt=plistlib.FMT_XML)
        zf.writestr('info.plist', plist_bytes)
        
    print(f"Created Alfred Workflow at: {workflow_path}")

if __name__ == "__main__":
    main()
