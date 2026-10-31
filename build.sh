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

echo "==> [1/3] Building React Frontend..."
cd frontend
npm install
npm run build
cd ..

echo "==> [2/3] Installing Python Backend Dependencies..."
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "==> [3/3] Build finished successfully!"
