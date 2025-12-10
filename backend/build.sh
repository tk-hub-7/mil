#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create demo bases (will skip if already exist)
python manage.py create_demo_bases

# Create demo users (will skip if already exist)
python manage.py create_demo_users
