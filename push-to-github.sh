#!/bin/bash
# Quick script to push Mini Fail2Ban to GitHub

set -e

echo "================================"
echo "Push Mini Fail2Ban to GitHub"
echo "================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "[1/5] Initializing Git repository..."
    git init
else
    echo "[1/5] Git repository already initialized"
fi

# Add all files
echo "[2/5] Adding files to Git..."
git add .

# Show status
echo ""
echo "Files to be committed:"
git status --short
echo ""

# Commit
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Initial commit: Mini Fail2Ban v1.0.0"
fi

echo "[3/5] Creating commit..."
git commit -m "$COMMIT_MSG" || echo "No changes to commit"

# Set main branch
git branch -M main

# Ask for remote URL
echo ""
echo "[4/5] Setting up remote repository..."
if git remote | grep -q "origin"; then
    echo "Remote 'origin' already exists:"
    git remote -v
    read -p "Do you want to update it? (y/N): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ] || [ "$UPDATE_REMOTE" = "Y" ]; then
        read -p "Enter GitHub repository URL: " REPO_URL
        git remote set-url origin "$REPO_URL"
    fi
else
    read -p "Enter GitHub repository URL (e.g., git@github.com:username/mini-fail2ban.git): " REPO_URL
    git remote add origin "$REPO_URL"
fi

# Push to GitHub
echo ""
echo "[5/5] Pushing to GitHub..."
read -p "Ready to push? (y/N): " CONFIRM
if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    git push -u origin main
    echo ""
    echo "================================"
    echo "Successfully pushed to GitHub!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Add description and topics"
    echo "3. Create a release (optional)"
    echo ""
else
    echo "Push cancelled. You can push manually with:"
    echo "  git push -u origin main"
fi
