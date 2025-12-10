@echo off
REM Batch script to run migrations on Render database from local machine

echo ========================================
echo Running Migrations on Render Database
echo ========================================
echo.

echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/5] Checking dependencies...
pip show psycopg2-binary >nul 2>&1
if errorlevel 1 (
    echo   Installing psycopg2-binary...
    pip install psycopg2-binary
) else (
    echo   psycopg2 is already installed
)

echo [3/5] Setting DATABASE_URL to Render PostgreSQL...
set DATABASE_URL=postgresql://postgres_28vl_user:37xfqXz2VJmdMDMAPWaiafst1DZXjOtC@dpg-d4sgsns9c44c73emakm0-a/postgres_28vl
echo   Connected to Render database

echo.
echo [4/5] Checking current migration status...
echo.
python manage.py showmigrations

echo.
echo [5/5] Running migrations...
echo.
python manage.py migrate

echo.
echo ========================================
echo Verifying migrations...
echo ========================================
echo.
python manage.py showmigrations

echo.
echo ========================================
echo DONE! Migrations completed!
echo ========================================
echo.
echo Next steps:
echo 1. Test your API: https://mil-2.onrender.com/api/v1/bases/
echo 2. Optionally seed demo data with: python manage.py seed_dummy_data
echo.

REM Cleanup
set DATABASE_URL=
pause
