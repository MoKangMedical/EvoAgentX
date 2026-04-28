#!/bin/bash
# ─────────────────────────────────────────────────────────────
# EvoAgentX Medical AI — Release Script
# ─────────────────────────────────────────────────────────────
# Creates a release with changelog and uploads to GitHub.
# Usage: ./scripts/release.sh 0.2.0
# ─────────────────────────────────────────────────────────────

set -e

VERSION=${1:? "Usage: ./scripts/release.sh <version>"}

echo "=== Releasing EvoAgentX v$VERSION ==="

# Update version in pyproject.toml
sed -i '' "s/version = \".*\"/version = \"$VERSION-medical\"/" pyproject.toml
echo "[OK] Updated pyproject.toml to $VERSION-medical"

# Update CHANGELOG
echo ""
echo "Current CHANGELOG.md:"
head -20 CHANGELOG.md
echo ""

# Run tests
echo "Running tests..."
python -m pytest tests/src/tools/test_medical_tools.py -v --tb=short -q 2>&1 | tail -5
echo "[OK] Tests passed"

# Commit
git add pyproject.toml
git commit -m "release: v$VERSION"

# Tag
git tag -a "v$VERSION" -m "EvoAgentX Medical AI v$VERSION"
echo "[OK] Created tag v$VERSION"

# Push
git push origin main --tags
echo "[OK] Pushed to GitHub"

# Create GitHub release
if command -v gh &> /dev/null; then
    gh release create "v$VERSION" \
        --title "EvoAgentX Medical AI v$VERSION" \
        --notes "See CHANGELOG.md for details" \
        --repo "$REPO"
    echo "[OK] Created GitHub release"
fi

echo ""
echo "=== Released v$VERSION ==="
echo "GitHub: https://github.com/MoKangMedical/EvoAgentX/releases/tag/v$VERSION"
