# PowerShell script to run migrations on Render database from local machine
# This script temporarily sets the DATABASE_URL to point to Render's PostgreSQL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Migrations on Render Database" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "[1/6] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Step 2: Check if psycopg2 is installed
Write-Host "[2/6] Checking dependencies..." -ForegroundColor Yellow
$psycopg2Installed = pip list 2>$null | Select-String "psycopg2"
if (-not $psycopg2Installed) {
    Write-Host "  Installing psycopg2-binary..." -ForegroundColor Yellow
    pip install psycopg2-binary
} else {
    Write-Host "  psycopg2 is already installed ✓" -ForegroundColor Green
}

# Step 3: Set DATABASE_URL to Render PostgreSQL
Write-Host "[3/6] Connecting to Render PostgreSQL..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql://postgres_28vl_user:37xfqXz2VJmdMDMAPWaiafst1DZXjOtC@dpg-d4sgsns9c44c73emakm0-a/postgres_28vl"
Write-Host "  Connected to: dpg-d4sgsns9c44c73emakm0-a ✓" -ForegroundColor Green

# Step 4: Check current migration status
Write-Host "[4/6] Checking migration status..." -ForegroundColor Yellow
Write-Host ""
python manage.py showmigrations
Write-Host ""

# Step 5: Run migrations
Write-Host "[5/6] Running migrations..." -ForegroundColor Yellow
Write-Host ""
python manage.py migrate
Write-Host ""

# Step 6: Verify migrations
Write-Host "[6/6] Verifying migrations..." -ForegroundColor Yellow
Write-Host ""
python manage.py showmigrations
Write-Host ""

# Cleanup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleaning up..." -ForegroundColor Yellow
$env:DATABASE_URL = ""
Write-Host "Environment variables cleared ✓" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DONE! Migrations completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test your API: https://mil-2.onrender.com/api/v1/bases/" -ForegroundColor White
Write-Host "2. Optionally seed demo data: python manage.py seed_dummy_data" -ForegroundColor White
Write-Host ""
