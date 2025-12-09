from django.core.management.base import BaseCommand
from assets.models import RoleCode


class Command(BaseCommand):
    help = 'Seed role codes for signup verification'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding role codes...')
        
        role_codes_data = [
            {
                'role': 'admin',
                'code': 'ADMIN-2024-SECURE',
                'description': 'Admin access code for full system control'
            },
            {
                'role': 'base_commander',
                'code': 'CMDR-BASE-7891',
                'description': 'Base Commander access code for base-specific management'
            },
            {
                'role': 'logistics_officer',
                'code': 'LOG-OFFICER-4523',
                'description': 'Logistics Officer access code for supply chain operations'
            },
        ]
        
        for code_data in role_codes_data:
            role_code, created = RoleCode.objects.get_or_create(
                role=code_data['role'],
                defaults={
                    'code': code_data['code'],
                    'description': code_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role code for {role_code.get_role_display()}: {role_code.code}'))
            else:
                self.stdout.write(f'Role code already exists for {role_code.get_role_display()}: {role_code.code}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Role codes seeded successfully!'))
        self.stdout.write('='*50)
        self.stdout.write('\nRole Codes:')
        for role_code in RoleCode.objects.filter(is_active=True):
            self.stdout.write(f'  {role_code.get_role_display()}: {role_code.code}')
