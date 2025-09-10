import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Salary_Management.settings')
django.setup()

# Create test users
from Dashboard.models import User as DashboardUser
from payslip_reportcard.models import ExtendedUser

print("Creating test users...")

# Create admin user
try:
    admin_user = DashboardUser.objects.create(
        username='admin',
        email='admin@payrollpro.com',
        password='admin123',
        first_names='Admin',
        last_names='User',
        phone_number='1234567890'
    )
    print(f'✓ Created admin user: {admin_user.username}')
    
    # Create extended user profile
    extended_user = ExtendedUser.objects.create(
        user=admin_user,
        role='Admin'
    )
    print(f'✓ Created ExtendedUser with role: {extended_user.role}')
    
except Exception as e:
    print(f'Admin user creation failed: {e}')

# Create HR user
try:
    hr_user = DashboardUser.objects.create(
        username='hr_user',
        email='hr@payrollpro.com',
        password='hr123',
        first_names='HR',
        last_names='Manager',
        phone_number='1234567891'
    )
    print(f'✓ Created HR user: {hr_user.username}')
    
    extended_user = ExtendedUser.objects.create(
        user=hr_user,
        role='HR'
    )
    print(f'✓ Created ExtendedUser with role: {extended_user.role}')
    
except Exception as e:
    print(f'HR user creation failed: {e}')

print('\n🎉 Test users setup complete!')
print('\n📝 Login credentials:')
print('Admin: admin / admin123')
print('HR: hr_user / hr123')
print('\nYou can now test login at: http://127.0.0.1:8000/simple_login.html')
