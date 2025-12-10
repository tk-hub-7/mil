"""
Management command to create demo user accounts for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assets.models import UserRole, Base


class Command(BaseCommand):
    help = 'Create demo user accounts with credentials'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating demo user accounts...'))
        
        # Demo user credentials
        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@military.com',
                'password': 'Admin@2024',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'assigned_base': None
            },
            {
                'username': 'commander',
                'email': 'commander@military.com',
                'password': 'Commander@2024',
                'first_name': 'Base',
                'last_name': 'Commander',
                'role': 'base_commander',
                'assigned_base': 'first'  # Will assign to first base
            },
            {
                'username': 'logistics',
                'email': 'logistics@military.com',
                'password': 'Logistics@2024',
                'first_name': 'Logistics',
                'last_name': 'Officer',
                'role': 'logistics_officer',
                'assigned_base': None
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in demo_users:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'User "{username}" already exists - skipping')
                skipped_count += 1
                continue
            
            # Get assigned base if specified
            assigned_base = None
            if user_data['assigned_base'] == 'first':
                assigned_base = Base.objects.filter(is_deleted=False).first()
                if not assigned_base:
                    self.stdout.write(self.style.WARNING(f'No bases found for {username} - creating without base'))
            
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Create user role
            UserRole.objects.create(
                user=user,
                role=user_data['role'],
                assigned_base=assigned_base
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created {user_data["role"]} user: {username} (password: {user_data["password"]})'
                )
            )
            created_count += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Demo users created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Users skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if created_count > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Demo Login Credentials:'))
            self.stdout.write('  Admin:')
            self.stdout.write('    Username: admin')
            self.stdout.write('    Password: Admin@2024')
            self.stdout.write('')
            self.stdout.write('  Base Commander:')
            self.stdout.write('    Username: commander')
            self.stdout.write('    Password: Commander@2024')
            self.stdout.write('')
            self.stdout.write('  Logistics Officer:')
            self.stdout.write('    Username: logistics')
            self.stdout.write('    Password: Logistics@2024')
