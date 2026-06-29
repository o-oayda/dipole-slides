#!/usr/bin/env bash
set -euo pipefail

port="${1:-8000}"
site_dir="_site"

rm -rf "$site_dir"
mkdir -p "$site_dir"

cp CNAME "$site_dir/" 2>/dev/null || true
cp -r assets "$site_dir/" 2>/dev/null || true

find slides -maxdepth 1 -type f -name "*.pdf" -exec cp {} "$site_dir/" \;
find slides -mindepth 1 -maxdepth 1 -type d -exec cp -r {} "$site_dir/" \;

python3 .github/scripts/build-index.py "$site_dir"

printf 'Previewing site at http://localhost:%s\n' "$port"
printf 'Press Ctrl+C to stop the server.\n'
python3 -m http.server "$port" --directory "$site_dir"
