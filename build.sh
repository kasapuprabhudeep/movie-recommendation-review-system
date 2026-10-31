#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=========================================="
echo "  Building Movie Recommendation System"
echo "=========================================="

# If inside parent folder, navigate into MovieRecommendationSystem
if [ -d "MovieRecommendationSystem" ]; then
  echo "==> Entering MovieRecommendationSystem folder..."
  cd MovieRecommendationSystem
fi

# Build React frontend (or use pre-built dist if available)
if [ -f "frontend/dist/index.html" ]; then
  echo "==> [1/2] Pre-built frontend dist detected! Skipping npm build..."
else
  echo "==> [1/2] Building React Frontend..."
  cd frontend
  npm install
  chmod -R +x node_modules/.bin 2>/dev/null || true
  npm run build
  cd ..
fi

echo "==> [2/2] Installing Python Backend Dependencies..."
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "==> Build finished successfully!"
