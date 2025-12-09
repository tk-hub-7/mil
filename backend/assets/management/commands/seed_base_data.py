from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assets.models import Base, EquipmentType
from datetime import datetime


class Command(BaseCommand):
    help = 'Seed the database with base data (bases, equipment types, and users)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with base data...')
        
        # Create Users with roles
        self.stdout.write('Creating users...')
        from assets.models import UserRole
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@military.gov',
                'password': 'admin123',
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin'
            },
            {
                'username': 'commander',
                'email': 'commander@military.gov',
                'password': 'commander123',
                'is_staff': True,
                'role': 'base_commander'
            },
            {
                'username': 'logistics',
                'email': 'logistics@military.gov',
                'password': 'logistics123',
                'is_staff': True,
                'role': 'logistics_officer'
            },
            {
                'username': 'officer1',
                'email': 'officer1@military.gov',
                'password': 'password123',
                'is_staff': True,
                'role': 'logistics_officer'
            },
            {
                'username': 'officer2',
                'email': 'officer2@military.gov',
                'password': 'password123',
                'is_staff': True,
                'role': 'logistics_officer'
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False)
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                # Update password for existing users
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Updated password for user: {user.username}')
            
            # Create or update UserRole
            user_role, role_created = UserRole.objects.get_or_create(
                user=user,
                defaults={'role': user_data['role']}
            )
            if not role_created and user_role.role != user_data['role']:
                user_role.role = user_data['role']
                user_role.save()
                self.stdout.write(f'Updated role for {user.username} to {user_data["role"]}')
        
        # Create Bases
        self.stdout.write('\nCreating military bases...')
        bases_data = [
            {'name': 'Fort Liberty', 'location': 'North Carolina', 'code': 'FL-NC'},
            {'name': 'Joint Base Lewis-McChord', 'location': 'Washington', 'code': 'JBLM-WA'},
            {'name': 'Fort Bragg', 'location': 'North Carolina', 'code': 'FB-NC'},
            {'name': 'Naval Base San Diego', 'location': 'California', 'code': 'NBSD-CA'},
            {'name': 'Wright-Patterson AFB', 'location': 'Ohio', 'code': 'WPAFB-OH'},
            {'name': 'Camp Pendleton', 'location': 'California', 'code': 'CP-CA'},
            {'name': 'Fort Hood', 'location': 'Texas', 'code': 'FH-TX'},
            {'name': 'Naval Station Norfolk', 'location': 'Virginia', 'code': 'NSN-VA'},
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
                self.stdout.write(self.style.SUCCESS(f'Created base: {base.name}'))
            else:
                self.stdout.write(f'Base already exists: {base.name}')
        
        # Create Equipment Types
        self.stdout.write('\nCreating equipment types...')
        equipment_types_data = [
            {'name': 'M4 Carbine', 'description': 'Standard issue assault rifle', 'unit': 'units'},
            {'name': 'M16 Rifle', 'description': 'Military rifle', 'unit': 'units'},
            {'name': 'M9 Pistol', 'description': 'Standard issue sidearm', 'unit': 'units'},
            {'name': 'Body Armor', 'description': 'Protective body armor', 'unit': 'units'},
            {'name': 'Kevlar Helmet', 'description': 'Ballistic helmet', 'unit': 'units'},
            {'name': 'Night Vision Goggles', 'description': 'Night vision equipment', 'unit': 'units'},
            {'name': 'Tactical Radio', 'description': 'Communication device', 'unit': 'units'},
            {'name': 'GPS Device', 'description': 'Navigation equipment', 'unit': 'units'},
            {'name': 'Medical Kit', 'description': 'First aid supplies', 'unit': 'kits'},
            {'name': 'Combat Boots', 'description': 'Military footwear', 'unit': 'pairs'},
            {'name': 'Tactical Vest', 'description': 'Load-bearing vest', 'unit': 'units'},
            {'name': 'Ammunition 5.56mm', 'description': 'Rifle ammunition', 'unit': 'rounds'},
            {'name': 'Ammunition 9mm', 'description': 'Pistol ammunition', 'unit': 'rounds'},
            {'name': 'Grenade Launcher', 'description': 'Grenade launching system', 'unit': 'units'},
            {'name': 'Binoculars', 'description': 'Optical viewing device', 'unit': 'units'},
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
                self.stdout.write(self.style.SUCCESS(f'Created equipment: {equipment.name}'))
            else:
                self.stdout.write(f'Equipment already exists: {equipment.name}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Base data created successfully!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\nUsers: {User.objects.count()}')
        self.stdout.write(f'Bases: {Base.objects.count()}')
        self.stdout.write(f'Equipment Types: {EquipmentType.objects.count()}')
        self.stdout.write('\n' + self.style.WARNING('Default password for all users: password123'))
        self.stdout.write(self.style.WARNING('Please change passwords in production!'))
