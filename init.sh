#!/usr/bin/env bash
set -euo pipefail

NAME="${1:?Usage: ./init.sh <project-name>}"

# Validate: lowercase alphanumeric with hyphens
if ! [[ "$NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
  echo "Error: project name must be lowercase alphanumeric with hyphens (e.g. my-app)"
  exit 1
fi

echo "Replacing __PROJECT_NAME__ with '$NAME' across all files..."

# macOS-compatible sed (uses -i '' instead of -i)
find . -type f \
  -not -path './.git/*' \
  -not -name 'init.sh' \
  -not -name '*.png' \
  -not -name '*.jpg' \
  -not -name '*.ico' \
  -not -name '*.woff' \
  -not -name '*.woff2' \
  -exec sed -i '' "s/__PROJECT_NAME__/$NAME/g" {} +

echo "✓ Replaced __PROJECT_NAME__ with '$NAME'"
echo ""
echo "Next steps:"
echo "  1. npm install"
echo "  2. cp server/.env.example server/.env"
echo "  3. npm run dev  (frontend)  +  cd server && uvicorn app.main:app --reload  (backend)"
echo "  4. Or: docker compose up --build"
echo ""
echo "You can now delete this script: rm init.sh"
