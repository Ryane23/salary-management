#!/usr/bin/env python
"""
Create Sample Employee Data
===========================
This script creates sample employee data for testing the employee management interface.
It creates a company, users, and employees with various roles and departments.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Salary_Management.settings')
django.setup()

from Dashboard.models import User
from payslip_reportcard.models import Company, ExtendedUser, PayrollEmployee
from django.contrib.auth.hashers import make_password

def create_sample_data():
    """Create sample data for employee management testing"""
    
    # Create or get company
    company, created = Company.objects.get_or_create(
        name="TechCorp Solutions",
        defaults={
            'bank_balance': Decimal('500000.00')
        }
    )
    
    if created:
        print(f"✓ Created company: {company.name}")
    else:
        print(f"✓ Using existing company: {company.name}")
    
    # Sample employee data
    employees_data = [
        {
            'username': 'john.doe',
            'email': 'john.doe@techcorp.com',
            'first_names': 'John',
            'last_names': 'Doe',
            'phone_number': '+1-555-0101',
            'role': 'Software Engineer',
            'base_salary': Decimal('75000.00'),
            'bank_name': 'Chase Bank',
            'bank_account': '1234567890',
            'is_active': True
        },
        {
            'username': 'jane.smith',
            'email': 'jane.smith@techcorp.com',
            'first_names': 'Jane',
            'last_names': 'Smith',
            'phone_number': '+1-555-0102',
            'role': 'Product Manager',
            'base_salary': Decimal('85000.00'),
            'bank_name': 'Bank of America',
            'bank_account': '2345678901',
            'is_active': True
        },
        {
            'username': 'mike.johnson',
            'email': 'mike.johnson@techcorp.com',
            'first_names': 'Mike',
            'last_names': 'Johnson',
            'phone_number': '+1-555-0103',
            'role': 'DevOps Engineer',
            'base_salary': Decimal('78000.00'),
            'bank_name': 'Wells Fargo',
            'bank_account': '3456789012',
            'is_active': True
        },
        {
            'username': 'sarah.wilson',
            'email': 'sarah.wilson@techcorp.com',
            'first_names': 'Sarah',
            'last_names': 'Wilson',
            'phone_number': '+1-555-0104',
            'role': 'UX Designer',
            'base_salary': Decimal('70000.00'),
            'bank_name': 'Chase Bank',
            'bank_account': '4567890123',
            'is_active': True
        },
        {
            'username': 'david.brown',
            'email': 'david.brown@techcorp.com',
            'first_names': 'David',
            'last_names': 'Brown',
            'phone_number': '+1-555-0105',
            'role': 'Senior Software Engineer',
            'base_salary': Decimal('95000.00'),
            'bank_name': 'Bank of America',
            'bank_account': '5678901234',
            'is_active': True
        },
        {
            'username': 'lisa.garcia',
            'email': 'lisa.garcia@techcorp.com',
            'first_names': 'Lisa',
            'last_names': 'Garcia',
            'phone_number': '+1-555-0106',
            'role': 'Data Scientist',
            'base_salary': Decimal('88000.00'),
            'bank_name': 'Wells Fargo',
            'bank_account': '6789012345',
            'is_active': True
        },
        {
            'username': 'robert.davis',
            'email': 'robert.davis@techcorp.com',
            'first_names': 'Robert',
            'last_names': 'Davis',
            'phone_number': '+1-555-0107',
            'role': 'QA Engineer',
            'base_salary': Decimal('65000.00'),
            'bank_name': 'Chase Bank',
            'bank_account': '7890123456',
            'is_active': True
        },
        {
            'username': 'emily.martinez',
            'email': 'emily.martinez@techcorp.com',
            'first_names': 'Emily',
            'last_names': 'Martinez',
            'phone_number': '+1-555-0108',
            'role': 'Marketing Specialist',
            'base_salary': Decimal('60000.00'),
            'bank_name': 'Bank of America',
            'bank_account': '8901234567',
            'is_active': False  # Inactive employee
        },
        {
            'username': 'chris.taylor',
            'email': 'chris.taylor@techcorp.com',
            'first_names': 'Chris',
            'last_names': 'Taylor',
            'phone_number': '+1-555-0109',
            'role': 'HR Manager',
            'base_salary': Decimal('72000.00'),
            'bank_name': 'Wells Fargo',
            'bank_account': '9012345678',
            'is_active': True
        },
        {
            'username': 'amanda.lee',
            'email': 'amanda.lee@techcorp.com',
            'first_names': 'Amanda',
            'last_names': 'Lee',
            'phone_number': '+1-555-0110',
            'role': 'Frontend Developer',
            'base_salary': Decimal('73000.00'),
            'bank_name': 'Chase Bank',
            'bank_account': '0123456789',
            'is_active': True
        }
    ]
    
    created_count = 0
    
    for emp_data in employees_data:
        # Check if user already exists
        if User.objects.filter(username=emp_data['username']).exists():
            print(f"  - User {emp_data['username']} already exists, skipping...")
            continue
        
        try:
            # Create Dashboard.User
            user = User.objects.create(
                username=emp_data['username'],
                email=emp_data['email'],
                first_names=emp_data['first_names'],
                last_names=emp_data['last_names'],
                phone_number=emp_data['phone_number'],
                password=make_password('password123')  # Default password for all test users
            )
            
            # Create PayrollEmployee
            employee = PayrollEmployee.objects.create(
                user=user,
                company=company,
                phone=emp_data['phone_number'],
                role=emp_data['role'],
                base_salary=emp_data['base_salary'],
                bank_name=emp_data['bank_name'],
                bank_account_number=emp_data['bank_account'],
                is_active=emp_data['is_active']
            )
            
            created_count += 1
            status = "✓" if emp_data['is_active'] else "○"
            print(f"  {status} Created employee: {emp_data['first_names']} {emp_data['last_names']} ({emp_data['role']})")
            
        except Exception as e:
            print(f"  ✗ Error creating employee {emp_data['username']}: {str(e)}")
    
    print(f"\n✓ Successfully created {created_count} employees")
    
    # Create admin user if not exists
    if not User.objects.filter(username='admin').exists():
        try:
            admin_user = User.objects.create(
                username='admin',
                email='admin@techcorp.com',
                first_names='Admin',
                last_names='User',
                phone_number='+1-555-0001',
                password=make_password('admin123')
            )
            
            # Create ExtendedUser for admin
            admin_extended = ExtendedUser.objects.create(
                user=admin_user,
                role='Admin',
                company=company
            )
            
            print(f"✓ Created admin user: admin / admin123")
            
        except Exception as e:
            print(f"✗ Error creating admin user: {str(e)}")
    else:
        print("✓ Admin user already exists")
    
    # Print summary
    total_employees = PayrollEmployee.objects.filter(company=company).count()
    active_employees = PayrollEmployee.objects.filter(company=company, is_active=True).count()
    departments = PayrollEmployee.objects.filter(company=company).values_list('role', flat=True).distinct().count()
    
    print(f"\n📊 Company Summary:")
    print(f"   Company: {company.name}")
    print(f"   Total Employees: {total_employees}")
    print(f"   Active Employees: {active_employees}")
    print(f"   Departments/Roles: {departments}")
    print(f"   Company Balance: ${company.bank_balance:,.2f}")
    
    print(f"\n🔑 Login Credentials:")
    print(f"   Admin: admin / admin123")
    print(f"   All employees: [username] / password123")
    
    print(f"\n🌐 Access URLs:")
    print(f"   Dashboard: http://127.0.0.1:8000/dashboard_admin_new.html")
    print(f"   Employee Management: http://127.0.0.1:8000/employee_management.html")
    print(f"   API Endpoints: http://127.0.0.1:8000/api/")

if __name__ == '__main__':
    print("Creating sample employee data...")
    print("=" * 50)
    create_sample_data()
    print("=" * 50)
    print("✅ Sample data creation completed!")
