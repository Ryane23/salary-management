from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime
from .models import (
    Company, ExtendedUser, PayrollEmployee, 
    Payroll, PayrollNotification
)

User = get_user_model()

class CompanyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_names='Admin',
            last_names='User'
        )
        
    def test_company_creation(self):
        company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('100000.00'),
            created_by=self.user
        )
        self.assertEqual(company.name, 'Test Company')
        self.assertEqual(company.bank_balance, Decimal('100000.00'))
        
    def test_can_afford_payroll(self):
        company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('10000.00'),
            created_by=self.user
        )
        self.assertTrue(company.can_afford_payroll(Decimal('5000.00')))
        self.assertFalse(company.can_afford_payroll(Decimal('15000.00')))
        
    def test_deduct_payroll_amount(self):
        company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('10000.00'),
            created_by=self.user
        )
        
        # Successful deduction
        result = company.deduct_payroll_amount(Decimal('3000.00'))
        self.assertTrue(result)
        self.assertEqual(company.bank_balance, Decimal('7000.00'))
        
        # Insufficient funds
        result = company.deduct_payroll_amount(Decimal('10000.00'))
        self.assertFalse(result)
        self.assertEqual(company.bank_balance, Decimal('7000.00'))


class PayrollEmployeeModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_names='Admin',
            last_names='User'
        )
        
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            first_names='John',
            last_names='Doe'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('100000.00'),
            created_by=self.admin_user
        )
        
    def test_employee_creation(self):
        employee = PayrollEmployee.objects.create(
            user=self.employee_user,
            company=self.company,
            phone='1234567890',
            role='Developer',
            base_salary=Decimal('5000.00')
        )
        
        self.assertEqual(employee.full_name, 'John Doe')
        self.assertEqual(employee.base_salary, Decimal('5000.00'))
        self.assertTrue(employee.is_active)


class PayrollModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_names='Admin',
            last_names='User'
        )
        
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            first_names='John',
            last_names='Doe'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('100000.00'),
            created_by=self.admin_user
        )
        
        self.employee = PayrollEmployee.objects.create(
            user=self.employee_user,
            company=self.company,
            phone='1234567890',
            role='Developer',
            base_salary=Decimal('5000.00')
        )
        
    def test_payroll_creation_and_calculation(self):
        payroll = Payroll.objects.create(
            employee=self.employee,
            attendance_days=22,
            bonus=Decimal('1000.00'),
            deductions=Decimal('200.00'),
            month=1,
            year=2024,
            created_by=self.admin_user
        )
        
        # Test auto-calculation of final_salary
        expected_final = self.employee.base_salary + payroll.bonus - payroll.deductions
        self.assertEqual(payroll.final_salary, expected_final)
        self.assertEqual(payroll.status, 'Pending')
        
    def test_payroll_approval(self):
        payroll = Payroll.objects.create(
            employee=self.employee,
            attendance_days=22,
            bonus=Decimal('1000.00'),
            deductions=Decimal('200.00'),
            month=1,
            year=2024,
            created_by=self.admin_user
        )
        
        initial_balance = self.company.bank_balance
        result = payroll.approve_payroll(self.admin_user)
        
        self.assertTrue(result)
        self.assertEqual(payroll.status, 'Approved')
        self.assertEqual(payroll.approved_by, self.admin_user)
        
        # Check if company balance was deducted
        self.company.refresh_from_db()
        self.assertEqual(
            self.company.bank_balance, 
            initial_balance - payroll.final_salary
        )
        
    def test_payroll_approval_insufficient_funds(self):
        # Set low company balance
        self.company.bank_balance = Decimal('1000.00')
        self.company.save()
        
        payroll = Payroll.objects.create(
            employee=self.employee,
            attendance_days=22,
            bonus=Decimal('1000.00'),
            deductions=Decimal('200.00'),
            month=1,
            year=2024,
            created_by=self.admin_user
        )
        
        with self.assertRaises(ValueError):
            payroll.approve_payroll(self.admin_user)
            
        # Status should remain Pending
        self.assertEqual(payroll.status, 'Pending')
        
    def test_mark_as_paid(self):
        payroll = Payroll.objects.create(
            employee=self.employee,
            attendance_days=22,
            bonus=Decimal('1000.00'),
            deductions=Decimal('200.00'),
            month=1,
            year=2024,
            created_by=self.admin_user,
            status='Approved'
        )
        
        result = payroll.mark_as_paid()
        self.assertTrue(result)
        self.assertEqual(payroll.status, 'Paid')
        
    def test_mark_as_paid_not_approved(self):
        payroll = Payroll.objects.create(
            employee=self.employee,
            attendance_days=22,
            bonus=Decimal('1000.00'),
            deductions=Decimal('200.00'),
            month=1,
            year=2024,
            created_by=self.admin_user,
            status='Pending'
        )
        
        result = payroll.mark_as_paid()
        self.assertFalse(result)
        self.assertEqual(payroll.status, 'Pending')


class ExtendedUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            first_names='Test',
            last_names='User'
        )
        
    def test_extended_user_creation(self):
        extended_user = ExtendedUser.objects.create(
            user=self.user,
            role='HR'
        )
        
        self.assertEqual(extended_user.role, 'HR')
        self.assertTrue(extended_user.is_hr())
        self.assertFalse(extended_user.is_admin())
        self.assertFalse(extended_user.is_director())
        
    def test_role_checks(self):
        # Test Admin role
        admin = ExtendedUser.objects.create(user=self.user, role='Admin')
        self.assertTrue(admin.is_admin())
        self.assertFalse(admin.is_hr())
        self.assertFalse(admin.is_director())
        
        # Test Director role
        director = ExtendedUser.objects.create(
            user=User.objects.create_user(
                username='director',
                email='director@test.com',
                first_names='Director',
                last_names='User'
            ),
            role='Director'
        )
        self.assertTrue(director.is_director())
        self.assertFalse(director.is_admin())
        self.assertFalse(director.is_hr())


class PayrollNotificationModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            first_names='Admin',
            last_names='User'
        )
        
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            first_names='John',
            last_names='Doe'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            bank_balance=Decimal('100000.00'),
            created_by=self.admin_user
        )
        
        self.employee = PayrollEmployee.objects.create(
            user=self.employee_user,
            company=self.company,
            phone='1234567890',
            role='Developer',
            base_salary=Decimal('5000.00')
        )
        
    def test_notification_creation(self):
        notification = PayrollNotification.objects.create(
            employee=self.employee,
            message='Test notification message'
        )
        
        self.assertEqual(notification.employee, self.employee)
        self.assertEqual(notification.message, 'Test notification message')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.sent_at)


# Create your tests here.
