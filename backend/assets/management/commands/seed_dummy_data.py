from django.core.management.base import BaseCommand
from assets.models import Base, EquipmentType, RoleCode


class Command(BaseCommand):
    help = 'Seed database with dummy bases, equipment types, and role codes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with dummy data...\n')
        
        # Create Role Codes if they don't exist
        role_codes_data = [
            {'role': 'admin', 'code': 'ADMIN-2024-SECURE', 'description': 'Administrator access code'},
            {'role': 'base_commander', 'code': 'CMDR-BASE-7891', 'description': 'Base Commander access code'},
            {'role': 'logistics_officer', 'code': 'LOG-OFFICER-4523', 'description': 'Logistics Officer access code'},
        ]
        
        for role_data in role_codes_data:
            role_code, created = RoleCode.objects.get_or_create(
                role=role_data['role'],
                defaults={
                    'code': role_data['code'],
                    'description': role_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created role code: {role_data["role"]}'))
            else:
                self.stdout.write(f'  Role code already exists: {role_data["role"]}')
        
        # Create Bases if they don't exist
        bases_data = [
            {'name': 'Fort Alpha', 'code': 'FA-001', 'location': 'Northern Region'},
            {'name': 'Fort Bravo', 'code': 'FB-002', 'location': 'Southern Region'},
            {'name': 'Fort Charlie', 'code': 'FC-003', 'location': 'Eastern Region'},
            {'name': 'Fort Delta', 'code': 'FD-004', 'location': 'Western Region'},
            {'name': 'Fort Echo', 'code': 'FE-005', 'location': 'Central Region'},
            {'name': 'Naval Base Omega', 'code': 'NBO-006', 'location': 'Coastal Region'},
            {'name': 'Air Force Base Zulu', 'code': 'AFB-007', 'location': 'Highland Region'},
        ]
        
        for base_data in bases_data:
            base, created = Base.objects.get_or_create(
                code=base_data['code'],
                defaults={
                    'name': base_data['name'],
                    'location': base_data['location']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created base: {base_data["name"]} ({base_data["code"]})'))
            else:
                self.stdout.write(f'  Base already exists: {base_data["name"]}')
        
        # Create Equipment Types if they don't exist
        equipment_types_data = [
            {'name': 'M4 Carbine', 'description': 'Standard issue rifle', 'unit': 'units'},
            {'name': 'M9 Pistol', 'description': 'Standard issue sidearm', 'unit': 'units'},
            {'name': 'Body Armor', 'description': 'Protective vest', 'unit': 'units'},
            {'name': 'Helmet', 'description': 'Combat helmet', 'unit': 'units'},
            {'name': 'Night Vision Goggles', 'description': 'NVG equipment', 'unit': 'units'},
            {'name': 'Radio Equipment', 'description': 'Communication device', 'unit': 'units'},
            {'name': 'First Aid Kit', 'description': 'Medical supplies', 'unit': 'kits'},
            {'name': 'Ammunition (5.56mm)', 'description': 'Rifle ammunition', 'unit': 'rounds'},
            {'name': 'Ammunition (9mm)', 'description': 'Pistol ammunition', 'unit': 'rounds'},
            {'name': 'MRE (Meals Ready to Eat)', 'description': 'Field rations', 'unit': 'meals'},
        ]
        
        for eq_data in equipment_types_data:
            equipment, created = EquipmentType.objects.get_or_create(
                name=eq_data['name'],
                defaults={
                    'description': eq_data['description'],
                    'unit': eq_data['unit']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created equipment: {eq_data["name"]}'))
            else:
                self.stdout.write(f'  Equipment already exists: {eq_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding complete!'))
        self.stdout.write(f'Total Bases: {Base.objects.count()}')
        self.stdout.write(f'Total Equipment Types: {EquipmentType.objects.count()}')
        self.stdout.write(f'Total Role Codes: {RoleCode.objects.count()}')
