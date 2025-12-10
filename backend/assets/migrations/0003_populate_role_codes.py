"""
Data migration to create default RoleCode entries
"""
from django.db import migrations


def create_role_codes(apps, schema_editor):
    """Create default role codes for signup"""
    RoleCode = apps.get_model('assets', 'RoleCode')
    
    # Define default role codes
    role_codes = [
        {
            'role': 'admin',
            'code': 'ADMIN2024',
            'description': 'Administrator access code',
            'is_active': True
        },
        {
            'role': 'base_commander',
            'code': 'BASECMD2024',
            'description': 'Base Commander access code',
            'is_active': True
        },
        {
            'role': 'logistics_officer',
            'code': 'LOGISTICS2024',
            'description': 'Logistics Officer access code',
            'is_active': True
        },
    ]
    
    # Create role codes if they don't exist
    for role_data in role_codes:
        RoleCode.objects.get_or_create(
            role=role_data['role'],
            defaults={
                'code': role_data['code'],
                'description': role_data['description'],
                'is_active': role_data['is_active']
            }
        )


def reverse_role_codes(apps, schema_editor):
    """Remove role codes"""
    RoleCode = apps.get_model('assets', 'RoleCode')
    RoleCode.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_rolecode'),  # Adjust this to your latest migration
    ]

    operations = [
        migrations.RunPython(create_role_codes, reverse_role_codes),
    ]
