#!/bin/bash
# ─────────────────────────────────────────────────────────────
# EvoAgentX Medical AI — One-Click Push & Deploy
# ─────────────────────────────────────────────────────────────
# Creates GitHub repo, pushes code, enables Pages.
# Usage: ./scripts/push-and-deploy.sh
# ─────────────────────────────────────────────────────────────

set -e

REPO="MoKangMedical/EvoAgentX"
REMOTE_URL="https://github.com/$REPO.git"

echo "============================================"
echo "  EvoAgentX — Push & Deploy"
echo "============================================"
echo ""

# Step 1: Check if repo exists
echo "[1/5] Checking GitHub repo..."
if git ls-remote "$REMOTE_URL" 2>/dev/null | head -1 > /dev/null 2>&1; then
    echo "  [OK] Repo exists at $REMOTE_URL"
else
    echo "  [!] Repo not found. Please create it manually:"
    echo ""
    echo "  1. Open: https://github.com/new"
    echo "  2. Name: EvoAgentX"
    echo "  3. Description: Self-Evolving Medical AI Agent Framework"
    echo "  4. Public"
    echo "  5. Do NOT add README/LICENSE"
    echo "  6. Click 'Create repository'"
    echo ""
    read -p "  Press Enter after creating the repo..."
fi

# Step 2: Configure remote
echo ""
echo "[2/5] Configuring remote..."
git remote set-url origin "$REMOTE_URL" 2>/dev/null || git remote add origin "$REMOTE_URL"
echo "  [OK] Remote set to $REMOTE_URL"

# Step 3: Push
echo ""
echo "[3/5] Pushing code..."
git push -u origin main 2>&1
echo "  [OK] Pushed to GitHub"

# Step 4: Enable GitHub Pages
echo ""
echo "[4/5] Enabling GitHub Pages..."
echo "  Go to: https://github.com/$REPO/settings/pages"
echo "  Source: Deploy from a branch"
echo "  Branch: gh-pages (will be created by CI)"
echo "  Folder: / (root)"
echo "  Click Save"
echo ""
echo "  Or wait for the deploy-pages workflow to run automatically."

# Step 5: Summary
echo ""
echo "[5/5] Done!"
echo ""
echo "============================================"
echo "  URLs:"
echo "============================================"
echo "  Repo:    https://github.com/$REPO"
echo "  Pages:   https://mokangmedical.github.io/EvoAgentX/"
echo "  Actions: https://github.com/$REPO/actions"
echo ""
echo "  After Pages deploys (2-3 min), your landing page will be live!"
echo ""
