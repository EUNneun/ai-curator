#!/bin/bash
set -euo pipefail

SITE_DIR="output/site"

echo "=== GitHub Pages 배포 시작 ==="

if [ ! -f "$SITE_DIR/index.html" ]; then
  echo "ERROR: $SITE_DIR/index.html not found" >&2
  exit 1
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "ERROR: GITHUB_TOKEN not set" >&2
  exit 1
fi

if [ -z "${GITHUB_REPOSITORY:-}" ]; then
  echo "ERROR: GITHUB_REPOSITORY not set" >&2
  exit 1
fi

cd "$SITE_DIR"

git init
git config user.email "action@github.com"
git config user.name "GitHub Actions"
git checkout -b gh-pages

git add -A
git commit -m "Auto deploy: $(date -u '+%Y-%m-%d %H:%M UTC')"

git push --force \
  "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" \
  gh-pages

echo "=== 배포 완료 ==="
