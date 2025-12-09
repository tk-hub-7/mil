from django.contrib.auth.models import User

# Reset admin password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("✅ Admin password reset to: admin123")
except User.DoesNotExist:
    print("❌ Admin user not found")

# Reset commander password  
try:
    commander = User.objects.get(username='commander')
    commander.set_password('commander123')
    commander.save()
    print("✅ Commander password reset to: commander123")
except User.DoesNotExist:
    print("❌ Commander user not found")

# Reset logistics password
try:
    logistics = User.objects.get(username='logistics')
    logistics.set_password('logistics123')
    logistics.save()
    print("✅ Logistics password reset to: logistics123")
except User.DoesNotExist:
    print("❌ Logistics user not found")

print("\n✅ All passwords have been reset!")
print("You can now login with:")
print("  - admin / admin123")
print("  - commander / commander123")
print("  - logistics / logistics123")
