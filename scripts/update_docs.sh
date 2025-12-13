#!/usr/bin/env bash
set -euo pipefail
python scripts/generate_api_reference.py
echo "Docs updated."
