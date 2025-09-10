"""
SALARY/PAYMENT MANAGEMENT SYSTEM - PERMISSIONS
===============================================
This file defines custom permission classes for role-based access control.
Each permission class checks user roles and restricts access accordingly.

Permission Classes:
- IsAdmin: Full access to all system functions and data
- IsHR: Can manage employees and payrolls, set payment dates
- IsDirector: Can validate/approve payrolls and view company finances
- IsAdminOrReadOnly: Admin gets full access, others get read-only access

Usage in views:
permission_classes = [permissions.IsAuthenticated, IsAdmin]
"""

from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Admin users full access.
    
    Admin users have complete access to:
    - All company data and settings
    - All employee records
    - All payroll records
    - User management
    - System reports and analytics
    
    Error scenarios to check:
    - User not authenticated -> returns False
    - User has no ExtendedUser profile -> returns False  
    - User role is not 'Admin' -> returns False
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            # Try to access the user's extended profile and check admin role
            return request.user.extendeduser.is_admin()
        except AttributeError:
            # User doesn't have an ExtendedUser profile
            return False


class IsHR(permissions.BasePermission):
    """
    Custom permission for HR users and Admins.
    
    HR users can:
    - Manage employee records (create, update, view)
    - Create and manage payrolls
    - Set and change payment dates
    - View payroll reports for their company
    
    Note: Admin users also get HR permissions
    
    Error scenarios to check:
    - User not authenticated -> returns False
    - User has no ExtendedUser profile -> returns False
    - User role is neither 'HR' nor 'Admin' -> returns False
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            # HR users OR Admin users can access HR functions
            return extended_user.is_hr() or extended_user.is_admin()
        except AttributeError:
            # User doesn't have an ExtendedUser profile
            return False


class IsDirector(permissions.BasePermission):
    """
    Custom permission for Director users and Admins.
    
    Director users can:
    - Validate and approve payrolls
    - View company bank balance and financial data
    - Access payroll reports and analytics
    - View all employee data (read-only)
    
    Note: Admin users also get Director permissions
    
    Error scenarios to check:
    - User not authenticated -> returns False
    - User has no ExtendedUser profile -> returns False
    - User role is neither 'Director' nor 'Admin' -> returns False
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            # Director users OR Admin users can access Director functions
            return extended_user.is_director() or extended_user.is_admin()
        except AttributeError:
            # User doesn't have an ExtendedUser profile
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow Admin users full access,
    but restrict others to read-only operations.
    
    This is useful for data that everyone should see but only Admins should modify.
    
    Access levels:
    - Admin: Full CRUD access (GET, POST, PUT, PATCH, DELETE)
    - HR/Director: Read-only access (GET only)
    - Unauthenticated: No access
    
    Error scenarios to check:
    - User not authenticated -> returns False
    - User has no ExtendedUser profile -> GET only, no modifications
    - Non-admin trying to modify data -> returns False
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            
            # Admin users have full access
            if extended_user.is_admin():
                return True
            
            # Others only have read access
            return request.method in permissions.SAFE_METHODS
        except AttributeError:
            return False


class IsEmployeeOrManagerReadOnly(permissions.BasePermission):
    """
    Custom permission to allow employees to view their own data,
    and managers to view their company's data.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            
            # Admin can access all
            if extended_user.is_admin():
                return True
            
            # HR and Director can view company employees
            if extended_user.is_hr() or extended_user.is_director():
                if hasattr(obj, 'company'):
                    return obj.company == extended_user.company
                elif hasattr(obj, 'employee'):
                    return obj.employee.company == extended_user.company
            
            # Employee can view their own data
            if hasattr(obj, 'user'):
                return obj.user == request.user
            elif hasattr(obj, 'employee'):
                return obj.employee.user == request.user
            
            return False
        except AttributeError:
            return False


class CanApprovePayroll(permissions.BasePermission):
    """
    Custom permission for payroll approval.
    Only Directors can approve payrolls.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            return extended_user.is_director() or extended_user.is_admin()
        except AttributeError:
            return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            extended_user = request.user.extendeduser
            
            # Admin can approve any payroll
            if extended_user.is_admin():
                return True
            
            # Director can only approve payrolls from their company
            if extended_user.is_director():
                return obj.employee.company == extended_user.company
            
            return False
        except AttributeError:
            return False
