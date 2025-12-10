"""
Script to populate demo bases in production database.
Run this in Render shell: python populate_bases.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'military_ams.settings')
django.setup()

from assets.models import Base

# Demo bases data
bases_data = [
    {'name': 'Alpha Base', 'location': 'North Region', 'code': 'ALPHA-01'},
    {'name': 'Bravo Base', 'location': 'South Region', 'code': 'BRAVO-02'},
    {'name': 'Charlie Base', 'location': 'East Region', 'code': 'CHARLIE-03'},
    {'name': 'Fort Alpha', 'location': 'Northern Region', 'code': 'FA-001'},
    {'name': 'Fort Bravo', 'location': 'Southern Region', 'code': 'FB-002'},
    {'name': 'Fort Charlie', 'location': 'Eastern Region', 'code': 'FC-003'},
    {'name': 'Fort Delta', 'location': 'Western Region', 'code': 'FD-004'},
    {'name': 'Fort Echo', 'location': 'Central Region', 'code': 'FE-005'},
    {'name': 'Naval Base Omega', 'location': 'Coastal Region', 'code': 'NBO-006'},
    {'name': 'Air Force Base Zulu', 'location': 'Highland Region', 'code': 'AFB-007'},
]

created_count = 0
skipped_count = 0

print('Creating demo military bases...')
print('=' * 60)

for base_data in bases_data:
    # Check if base already exists
    if Base.objects.filter(code=base_data['code']).exists():
        print(f'Base "{base_data["name"]}" already exists - skipping')
        skipped_count += 1
        continue
    
    # Create base
    Base.objects.create(**base_data)
    print(f'✓ Created base: {base_data["name"]} ({base_data["code"]})')
    created_count += 1

# Summary
print('')
print('=' * 60)
print(f'Bases created: {created_count}')
print(f'Bases skipped: {skipped_count}')
print(f'Total bases: {Base.objects.filter(is_deleted=False).count()}')
print('=' * 60)
