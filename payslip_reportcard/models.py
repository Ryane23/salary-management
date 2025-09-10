"""
SALARY/PAYMENT MANAGEMENT SYSTEM - DATABASE MODELS
==================================================
This file contains all database models for the salary management system.
Each model is clearly documented with docstrings explaining its purpose and usage.

Models included:
- Company: Manages company information and bank balance
- ExtendedUser: Adds role information to Django users (Admin, HR, Director)
- PayrollEmployee: Employee information with salary, bonuses, and deductions
- Payroll: Main payroll processing model with auto-calculated final salary
- PayrollNotification: Notification system for payroll updates

Role Permissions:
- Admin: Full access to all tables and operations
- HR: Manages employees and payrolls, can set/change payment dates
- Director: Validates payroll and views company bank balance
"""

from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define user role choices for the system - controls access permissions
ROLE_CHOICES = [
    ('Admin', 'Admin'),        # System administrator with full access to all tables
    ('HR', 'HR'),              # HR manager - manages employees and payrolls
    ('Director', 'Director'),   # Director - approves payrolls and views company finances
]

# Define payroll status choices for tracking processing stages
PAYROLL_STATUS_CHOICES = [
    ('Pending', 'Pending'),    # Created but not yet approved by director
    ('Approved', 'Approved'),  # Approved by director but payment not yet processed
    ('Paid', 'Paid'),          # Payment has been processed and completed
]

class Company(models.Model):
    """Company model to manage company information and bank balance"""
    name = models.CharField(max_length=200, unique=True)
    bank_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Company's available funds for payroll"
    )
    created_by = models.ForeignKey('Dashboard.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def can_afford_payroll(self, total_amount):
        """Check if company can afford a specific payroll amount"""
        return self.bank_balance >= total_amount

    def deduct_payroll_amount(self, amount):
        """Deduct payroll amount from company balance"""
        if self.can_afford_payroll(amount):
            self.bank_balance -= amount
            self.save()
            return True
        return False


class ExtendedUser(models.Model):
    """
    Extended user model to add role information 
    
    This model extends the Dashboard User with payroll-specific information:
    - Role (Admin, HR, Director) for permission control
    - Company association for multi-company support
    - Creation timestamp for audit purposes
    """
    user = models.OneToOneField('Dashboard.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='HR')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def is_admin(self):
        """Check if user has Admin role"""
        return self.role == 'Admin'

    def is_hr(self):
        """Check if user has HR role"""
        return self.role == 'HR'

    def is_director(self):
        """Check if user has Director role"""
        return self.role == 'Director'


class PayrollEmployee(models.Model):
    """Extended employee model with payroll-specific information"""
    user = models.OneToOneField('Dashboard.User', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=100, help_text="Employee's job role")
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_names} {self.user.last_names} - {self.role}"

    @property
    def full_name(self):
        return f"{self.user.first_names} {self.user.last_names}"


class Payroll(models.Model):
    """Main payroll model for salary processing"""
    employee = models.ForeignKey(PayrollEmployee, on_delete=models.CASCADE)
    attendance_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of days employee attended work"
    )
    bonus = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    deductions = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    final_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        editable=False,
        help_text="Auto-calculated: base_salary + bonus - deductions"
    )
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=PAYROLL_STATUS_CHOICES, 
        default='Pending'
    )
    created_by = models.ForeignKey('Dashboard.User', on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        'Dashboard.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_payrolls'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    month = models.PositiveSmallIntegerField(
        choices=[(i, f"{i:02d}") for i in range(1, 13)]
    )
    year = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.month:02d}/{self.year} - {self.status}"

    def save(self, *args, **kwargs):
        """Auto-calculate final salary before saving"""
        self.final_salary = self.employee.base_salary + self.bonus - self.deductions
        super().save(*args, **kwargs)

    def approve_payroll(self, approved_by_user):
        """Approve payroll and deduct from company balance"""
        if self.status == 'Pending':
            company = self.employee.company
            if company.can_afford_payroll(self.final_salary):
                company.deduct_payroll_amount(self.final_salary)
                self.status = 'Approved'
                self.approved_by = approved_by_user
                self.save()
                
                # Create notification for employee
                PayrollNotification.objects.create(
                    employee=self.employee,
                    message=f"Your payroll for {self.month:02d}/{self.year} has been approved. Amount: ${self.final_salary}",
                    payroll=self
                )
                return True
            else:
                raise ValueError("Insufficient company funds for this payroll")
        return False

    def mark_as_paid(self):
        """Mark payroll as paid"""
        if self.status == 'Approved':
            self.status = 'Paid'
            self.save()
            
            # Create payment notification
            PayrollNotification.objects.create(
                employee=self.employee,
                message=f"Payment processed for {self.month:02d}/{self.year}. Amount: ${self.final_salary}",
                payroll=self
            )
            return True
        return False


class PayrollNotification(models.Model):
    """Notifications related to payroll processing"""
    employee = models.ForeignKey(PayrollEmployee, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Notification for {self.employee.full_name}: {self.message[:50]}..."


# Keep the original model for backward compatibility
class Payslip_Reportcard(models.Model):
    payslip = models.ForeignKey('payslip.Payslip', on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(choices=[(i, f"{i:02d}") for i in range(1, 13)], blank=False, null=False)
    year = models.PositiveSmallIntegerField(blank=False, null=False)

    def __str__(self):
        return f"{self.month:02d}/{self.year} - {self.payslip}"


# Signal to create ExtendedUser when Dashboard.User is created
@receiver(post_save, sender='Dashboard.User')
def create_extended_user(sender, instance, created, **kwargs):
    if created:
        ExtendedUser.objects.get_or_create(user=instance)
