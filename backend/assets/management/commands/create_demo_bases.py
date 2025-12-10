"""
Management command to create demo military bases
"""
from django.core.management.base import BaseCommand
from assets.models import Base


class Command(BaseCommand):
    help = 'Create demo military bases'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating demo military bases...'))
        
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
        
        for base_data in bases_data:
            # Check if base already exists
            if Base.objects.filter(code=base_data['code']).exists():
                self.stdout.write(f'Base "{base_data["name"]}" already exists - skipping')
                skipped_count += 1
                continue
            
            # Create base
            Base.objects.create(**base_data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created base: {base_data["name"]} ({base_data["code"]})')
            )
            created_count += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Bases created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Bases skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total bases: {Base.objects.filter(is_deleted=False).count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
