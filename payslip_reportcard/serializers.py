"""
SALARY/PAYMENT MANAGEMENT SYSTEM - SERIALIZERS
===============================================
This file contains Django REST Framework serializers for API data serialization.
Each serializer handles data validation and conversion between Python objects and JSON.

Serializers included:
- CompanySerializer: Handles company data with bank balance validation
- ExtendedUserSerializer: User data with role information
- PayrollEmployeeSerializer: Employee data with salary, bonuses, deductions
- PayrollSerializer: Payroll processing with auto-calculated final salary
- PayrollNotificationSerializer: Notification system data
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from .models import (
    Company, ExtendedUser, PayrollEmployee, 
    Payroll, PayrollNotification
)

User = get_user_model()

# Dashboard-specific serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_employees = serializers.IntegerField()
    monthly_payroll = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_approvals = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    recent_activity = serializers.ListField()

class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity items"""
    type = serializers.CharField()
    title = serializers.CharField()
    time = serializers.DateTimeField()
    icon = serializers.CharField()

class DepartmentSerializer(serializers.Serializer):
    """Serializer for department information"""
    name = serializers.CharField()
    employee_count = serializers.IntegerField()
    total_salary = serializers.DecimalField(max_digits=15, decimal_places=2)

class CompanyProfileSerializer(serializers.ModelSerializer):
    """Enhanced company profile serializer"""
    departments = DepartmentSerializer(many=True, read_only=True)
    total_employees = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'bank_balance', 'total_employees', 'departments', 'created_at', 'updated_at']

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company model
    Handles company information and bank balance management
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'bank_balance', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """Automatically assign the current user as creator when creating a company"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExtendedUserSerializer(serializers.ModelSerializer):
    """
    Serializer for ExtendedUser model
    Includes role-based access control information
    """
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ExtendedUser
        fields = ['id', 'user', 'username', 'full_name', 'role', 'company', 'created_at']
        read_only_fields = ['created_at']

    def get_full_name(self, obj):
        """Combine first and last names for display purposes"""
        return f"{obj.user.first_names} {obj.user.last_names}"


class PayrollEmployeeSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for PayrollEmployee model with user management
    Handles employee data including user creation/update, salary, bank details
    """
    user = serializers.SerializerMethodField(read_only=True)
    user_data = serializers.DictField(write_only=True, required=False)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PayrollEmployee
        fields = [
            'id', 'user', 'user_data', 'full_name', 'company', 
            'phone', 'role', 'base_salary', 'bank_name', 
            'bank_account_number', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at', 'company']

    def get_user(self, obj):
        """Return detailed user information for frontend"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'first_names': obj.user.first_names,
                'last_names': obj.user.last_names,
                'phone_number': obj.user.phone_number,
            }
        return None

    def get_full_name(self, obj):
        """Return full name of the employee"""
        if obj.user:
            return f"{obj.user.first_names} {obj.user.last_names}"
        return ""

    def create(self, validated_data):
        """Create employee with user data"""
        from Dashboard.models import User
        from django.contrib.auth.hashers import make_password
        
        user_data = validated_data.pop('user_data', {})
        request = self.context.get('request')
        
        # Get company from the requesting user
        if request and hasattr(request.user, 'extendeduser'):
            validated_data['company'] = request.user.extendeduser.company
        
        # Create the Dashboard.User first
        if user_data:
            # Hash password if provided
            if 'password' in user_data:
                user_data['password'] = make_password(user_data['password'])
            
            user = User.objects.create(**user_data)
            validated_data['user'] = user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update employee and user data"""
        user_data = validated_data.pop('user_data', {})
        
        # Update user data if provided
        if user_data and instance.user:
            for attr, value in user_data.items():
                if attr == 'password' and value:
                    from django.contrib.auth.hashers import make_password
                    value = make_password(value)
                setattr(instance.user, attr, value)
            instance.user.save()
        
        return super().update(instance, validated_data)


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    company_name = serializers.CharField(source='employee.company.name', read_only=True)
    final_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'company_name',
            'attendance_days', 'bonus', 'deductions', 'final_salary',
            'payment_date', 'status', 'created_by', 'approved_by',
            'created_at', 'updated_at', 'month', 'year'
        ]
        read_only_fields = ['final_salary', 'created_at', 'updated_at', 'approved_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PayrollApprovalSerializer(serializers.Serializer):
    """Serializer for payroll approval action"""
    payroll_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of payroll IDs to approve"
    )


class PayrollNotificationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = PayrollNotification
        fields = [
            'id', 'employee', 'employee_name', 'message', 
            'sent_at', 'is_read', 'payroll'
        ]
        read_only_fields = ['sent_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_employees = serializers.IntegerField()
    pending_payrolls = serializers.IntegerField()
    approved_payrolls = serializers.IntegerField()
    paid_payrolls = serializers.IntegerField()
    total_payroll_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    company_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    unread_notifications = serializers.IntegerField()


class CompanyFundsSerializer(serializers.Serializer):
    """Serializer for company funds view"""
    company_name = serializers.CharField()
    current_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payroll_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    remaining_after_payroll = serializers.DecimalField(max_digits=15, decimal_places=2)
    can_afford_pending = serializers.BooleanField()


# Updated RecentActivitySerializer for analytics
class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity items"""
    id = serializers.CharField()
    employee_name = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    status = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    date = serializers.DateTimeField()
    type = serializers.CharField()


# Enhanced CompanyProfileSerializer
class CompanyProfileSerializer(serializers.Serializer):
    """Enhanced company profile serializer with comprehensive data"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    bank_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_employees = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    departments = serializers.ListField(
        child=serializers.DictField(), 
        read_only=True
    )
