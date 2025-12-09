from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Reset demo user passwords'

    def handle(self, *args, **kwargs):
        # Reset admin password
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin password reset to: admin123'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Admin user not found'))

        # Reset commander password  
        try:
            commander = User.objects.get(username='commander')
            commander.set_password('commander123')
            commander.save()
            self.stdout.write(self.style.SUCCESS('✓ Commander password reset to: commander123'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Commander user not found'))

        # Reset logistics password
        try:
            logistics = User.objects.get(username='logistics')
            logistics.set_password('logistics123')
            logistics.save()
            self.stdout.write(self.style.SUCCESS('✓ Logistics password reset to: logistics123'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Logistics user not found'))

        self.stdout.write(self.style.SUCCESS('\n✓ Password reset complete!'))
        self.stdout.write('You can now login with:')
        self.stdout.write('  - admin / admin123')
        self.stdout.write('  - commander / commander123')
        self.stdout.write('  - logistics / logistics123')
