@echo off
REM Script to commit and push build.sh to GitHub

echo ========================================
echo Committing build.sh to GitHub
echo ========================================
echo.

echo [1/3] Adding build.sh to git...
git add build.sh render.yaml

echo [2/3] Committing changes...
git commit -m "Add automated build script for Render migrations"

echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Files pushed to GitHub
echo ========================================
echo.
echo Next steps:
echo 1. Go to Render Dashboard: https://dashboard.render.com
echo 2. Click on your 'mil-2' service
echo 3. Go to Settings tab
echo 4. Update Build Command to: chmod +x build.sh ^^^&^^^& ./build.sh
echo 5. Click 'Save Changes'
echo 6. Click 'Manual Deploy' - 'Deploy latest commit'
echo.
pause
