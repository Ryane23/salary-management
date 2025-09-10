"""
Simple script to create a test user for authentication testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Salary_Management.settings')
django.setup()

from django.contrib.auth.models import User
from payslip_reportcard.models import ExtendedUser

# Create a test admin user
try:
    # Create Django user
    user = User.objects.create_user(
        username='admin',
        email='admin@payrollpro.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(f"Created Django user: {user.username}")
    
    # Create extended user profile
    extended_user = ExtendedUser.objects.create(
        user=user,
        role='Admin'
    )
    print(f"Created ExtendedUser with role: {extended_user.role}")
    
except Exception as e:
    print(f"Error creating user: {e}")
    # If user already exists, just update password
    try:
        user = User.objects.get(username='admin')
        user.set_password('admin123')
        user.save()
        print("Updated existing admin user password")
    except Exception as e2:
        print(f"Error updating user: {e2}")

# Create HR test user
try:
    user = User.objects.create_user(
        username='hr_user',
        email='hr@payrollpro.com',
        password='hr123',
        first_name='HR',
        last_name='User'
    )
    
    extended_user = ExtendedUser.objects.create(
        user=user,
        role='HR'
    )
    print(f"Created HR user: {user.username}")
    
except Exception as e:
    print(f"HR user creation failed: {e}")

# Create Director test user
try:
    user = User.objects.create_user(
        username='director',
        email='director@payrollpro.com',
        password='director123',
        first_name='Director',
        last_name='User'
    )
    
    extended_user = ExtendedUser.objects.create(
        user=user,
        role='Director'
    )
    print(f"Created Director user: {user.username}")
    
except Exception as e:
    print(f"Director user creation failed: {e}")

print("\nTest users created successfully!")
print("Admin: admin / admin123")
print("HR: hr_user / hr123") 
print("Director: director / director123")
