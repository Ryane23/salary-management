"""
SALARY/PAYMENT MANAGEMENT SYSTEM - API VIEWS
============================================
Complete Django REST Framework API views for the salary management system.
All views include proper error handling, permissions, and detailed documentation.

Views included:
- Dashboard API endpoints for statistics and recent activity
- Employee management with department grouping
- Payroll processing with approval workflow
- Company profile management
- User authentication and role management
"""

from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db.models import Sum, Count, Q, Avg, Max, Min
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import connection
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .models import (
    Company, ExtendedUser, PayrollEmployee, 
    Payroll, PayrollNotification
)
from .serializers import (
    CompanySerializer, ExtendedUserSerializer, PayrollEmployeeSerializer,
    PayrollSerializer, PayrollApprovalSerializer, PayrollNotificationSerializer,
    DashboardStatsSerializer, CompanyFundsSerializer, DashboardStatsSerializer,
    RecentActivitySerializer, DepartmentSerializer, CompanyProfileSerializer
)
from .permissions import IsAdmin, IsHR, IsDirector, IsAdminOrReadOnly

# Additional permission classes for comprehensive access control
class IsHROrAdmin(permissions.BasePermission):
    """
    Permission class that allows access to HR and Admin users only.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'extendeduser'):
            return request.user.extendeduser.role in ['HR', 'Admin']
        return False


class IsAuthorizedUser(permissions.BasePermission):
    """
    Permission class that allows access to Admin, HR, and Director users.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'extendeduser'):
            return request.user.extendeduser.role in ['Admin', 'HR', 'Director']
        return False

# Setup logging for better error tracking
logger = logging.getLogger(__name__)


# =================================================================
# DASHBOARD API ENDPOINTS
# =================================================================

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the current user's role
    Returns different stats based on user permissions
    """
    try:
        # Get user's extended info
        extended_user = ExtendedUser.objects.get(user__username=request.user.username)
        
        # Base statistics
        total_employees = PayrollEmployee.objects.filter(is_active=True).count()
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Monthly payroll calculation
        monthly_payroll = Payroll.objects.filter(
            month=current_month,
            year=current_year,
            status__in=['Approved', 'Paid']
        ).aggregate(total=Sum('final_salary'))['total'] or 0
        
        # Pending approvals
        pending_approvals = Payroll.objects.filter(status='Pending').count()
        
        # Department count (unique departments from employees)
        departments = PayrollEmployee.objects.filter(is_active=True).values_list('role', flat=True).distinct()
        total_departments = len(set(dept.split(' - ')[0] if ' - ' in dept else dept for dept in departments))
        
        # Recent activity
        recent_activity = []
        
        # Recent employee additions
        recent_employees = PayrollEmployee.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:3]
        
        for emp in recent_employees:
            recent_activity.append({
                'type': 'employee_added',
                'title': f'New employee {emp.full_name} added',
                'time': emp.created_at,
                'icon': 'user-plus'
            })
        
        # Recent payroll processing
        recent_payrolls = Payroll.objects.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-updated_at')[:3]
        
        for payroll in recent_payrolls:
            if payroll.status == 'Approved':
                recent_activity.append({
                    'type': 'payroll_approved',
                    'title': f'Payroll approved for {payroll.employee.full_name}',
                    'time': payroll.updated_at,
                    'icon': 'check-circle'
                })
            elif payroll.status == 'Paid':
                recent_activity.append({
                    'type': 'payroll_paid',
                    'title': f'Payment processed for {payroll.employee.full_name}',
                    'time': payroll.updated_at,
                    'icon': 'credit-card'
                })
        
        # Sort recent activity by time
        recent_activity.sort(key=lambda x: x['time'], reverse=True)
        recent_activity = recent_activity[:5]  # Keep only 5 most recent
        
        stats = {
            'total_employees': total_employees,
            'monthly_payroll': monthly_payroll,
            'pending_approvals': pending_approvals,
            'total_departments': total_departments,
            'recent_activity': recent_activity
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except ExtendedUser.DoesNotExist:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Dashboard stats error: {str(e)}")
        return Response(
            {'error': 'Failed to fetch dashboard statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def company_profile(request):
    """
    Get company profile with departments breakdown
    """
    try:
        # For single company setup, get the first company or create default
        company = Company.objects.first()
        if not company:
            # Create default company if none exists
            company = Company.objects.create(
                name="PayrollPro Solutions Inc.",
                bank_balance=1000000.00,
                created_by_id=1  # Assuming admin user ID 1
            )
        
        # Get departments with employee counts
        departments_data = defaultdict(lambda: {'count': 0, 'total_salary': 0})
        
        employees = PayrollEmployee.objects.filter(is_active=True)
        for emp in employees:
            # Extract department from role
            dept_name = emp.role.split(' - ')[0] if ' - ' in emp.role else 'General'
            departments_data[dept_name]['count'] += 1
            departments_data[dept_name]['total_salary'] += emp.base_salary
        
        # Convert to list format
        departments = []
        for dept_name, data in departments_data.items():
            departments.append({
                'name': dept_name,
                'employee_count': data['count'],
                'total_salary': data['total_salary']
            })
        
        # Company info with additional details
        profile_data = {
            'id': company.id,
            'name': company.name,
            'industry': 'Software & Technology',
            'founded': '2020',
            'headquarters': 'New York, NY',
            'email': 'info@payrollpro.com',
            'phone': '+1 (555) 123-4567',
            'website': 'www.payrollpro.com',
            'mission': 'To provide innovative and reliable payroll management solutions that streamline HR processes and ensure accurate, timely compensation for all employees.',
            'bank_balance': company.bank_balance,
            'total_employees': employees.count(),
            'departments': departments,
            'created_at': company.created_at,
            'updated_at': company.updated_at
        }
        
        return Response(profile_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Company profile error: {str(e)}")
        return Response(
            {'error': 'Failed to fetch company profile'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =================================================================
# DATABASE CONNECTIVITY TEST ENDPOINT
# =================================================================
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def test_db_connection(request):
    """
    Clean, organized API endpoint to test database connection.
    
    Authentication:
        - Requires TokenAuthentication
        - Must provide valid token in Authorization header: "Token <token_value>"
        - Returns 401 if no credentials provided
    
    Purpose:
        - Tests if database connection is working properly
        - Performs basic database operations to verify connectivity
        - Returns success/failure status with informative messages
    
    Returns:
        Success (200): {"status": "success", "message": "Database connection successful"}
        Failure (500): {"status": "error", "message": "Database connection failed: <error_message>"}
        Unauthorized (401): {"detail": "Authentication credentials were not provided."}
    
    Usage:
        GET /api/test-db/
        Headers: Authorization: Token <your_token_here>
    """
    try:
        # Log the database test attempt
        logger.info(f"Database connection test requested by user: {request.user.username}")
        
        # Test 1: Basic database connection check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Test 2: Simple query on a core model to ensure tables exist
        Company.objects.exists()
        
        # Test 3: Verify we can perform basic database operations
        user_count = ExtendedUser.objects.count()
        
        # Log successful test
        logger.info(f"Database connection test successful for user: {request.user.username}")
        
        # Return success response
        return Response({
            'status': 'success',
            'message': 'Database connection successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Log the error for debugging
        error_message = str(e)
        logger.error(f"Database connection test failed for user {request.user.username}: {error_message}")
        
        # Return detailed error response
        return Response({
            'status': 'error',
            'message': f'Database connection failed: {error_message}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =================================================================
# PUBLIC TESTING ENDPOINTS (NO AUTHENTICATION REQUIRED)
# =================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_test_db_connection(request):
    """
    Public endpoint to test database connection without authentication.
    For testing purposes only.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Test basic model operations
        Company.objects.exists()
        employee_count = PayrollEmployee.objects.count()
        company_count = Company.objects.count()
        
        return Response({
            'status': 'success',
            'message': 'Database connection successful',
            'data': {
                'employees': employee_count,
                'companies': company_count,
                'database_test': 'passed'
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_test_employees(request):
    """
    Public endpoint to test employee data loading without authentication.
    For testing purposes only.
    """
    try:
        # Get all employees with basic user data
        employees = PayrollEmployee.objects.select_related('user', 'company').all()
        
        employee_data = []
        for emp in employees:
            employee_data.append({
                'id': emp.id,
                'user': {
                    'first_names': emp.user.first_names,
                    'last_names': emp.user.last_names,
                    'username': emp.user.username,
                    'email': emp.user.email,
                    'phone_number': emp.user.phone_number,
                } if emp.user else None,
                'role': emp.role,
                'base_salary': str(emp.base_salary),
                'is_active': emp.is_active,
                'created_at': emp.created_at,
                'company_name': emp.company.name if emp.company else None
            })
        
        return Response({
            'status': 'success',
            'message': f'Loaded {len(employee_data)} employees',
            'data': employee_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load employees: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_test_departments(request):
    """
    Public endpoint to test department data loading without authentication.
    For testing purposes only.
    """
    try:
        # Get department statistics
        departments = PayrollEmployee.objects.values('role').annotate(
            employee_count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True)),
            total_salary=Sum('base_salary'),
            avg_salary=Avg('base_salary')
        ).order_by('role')
        
        department_data = []
        for dept in departments:
            department_data.append({
                'department': dept['role'],
                'employee_count': dept['employee_count'],
                'active_count': dept['active_count'],
                'total_salary': float(dept['total_salary'] or 0),
                'avg_salary': float(dept['avg_salary'] or 0)
            })
        
        return Response({
            'status': 'success',
            'message': f'Loaded {len(department_data)} departments',
            'data': department_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load departments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_dashboard_stats(request):
    """
    Public endpoint to test dashboard statistics without authentication.
    For testing purposes only.
    """
    try:
        # Calculate basic statistics
        total_employees = PayrollEmployee.objects.count()
        active_employees = PayrollEmployee.objects.filter(is_active=True).count()
        total_companies = Company.objects.count()
        
        # Calculate salary statistics
        salary_stats = PayrollEmployee.objects.aggregate(
            total_salary_cost=Sum('base_salary'),
            avg_salary=Avg('base_salary'),
            max_salary=Max('base_salary'),
            min_salary=Min('base_salary')
        )
        
        # Get company data
        company_balance = Company.objects.aggregate(
            total_balance=Sum('bank_balance')
        )['total_balance'] or 0
        
        stats = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': total_employees - active_employees,
            'total_companies': total_companies,
            'total_salary_cost': float(salary_stats['total_salary_cost'] or 0),
            'avg_salary': float(salary_stats['avg_salary'] or 0),
            'max_salary': float(salary_stats['max_salary'] or 0),
            'min_salary': float(salary_stats['min_salary'] or 0),
            'company_balance': float(company_balance)
        }
        
        return Response({
            'status': 'success',
            'message': 'Dashboard statistics loaded successfully',
            'data': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load dashboard stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def test_db_public(request):
    """
    Public database connection test endpoint for dashboard testing.
    No authentication required - for testing purposes only.
    
    Returns basic database connection status and employee count.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Get basic stats
        company_count = Company.objects.count()
        employee_count = PayrollEmployee.objects.count()
        user_count = ExtendedUser.objects.count()
        
        return Response({
            'status': 'success',
            'message': 'Database connection successful',
            'stats': {
                'companies': company_count,
                'employees': employee_count,
                'users': user_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def employees_public(request):
    """
    Public employee list endpoint for dashboard testing.
    No authentication required - returns all employees for testing.
    """
    try:
        employees = PayrollEmployee.objects.select_related('user', 'company').all()
        employee_data = []
        
        for emp in employees:
            employee_data.append({
                'id': emp.id,
                'user': {
                    'id': emp.user.id,
                    'username': emp.user.username,
                    'email': emp.user.email,
                    'first_names': emp.user.first_names,
                    'last_names': emp.user.last_names,
                    'phone_number': emp.user.phone_number,
                },
                'company': emp.company.name if emp.company else None,
                'phone': emp.phone,
                'role': emp.role,
                'base_salary': str(emp.base_salary),
                'bank_name': emp.bank_name,
                'bank_account_number': emp.bank_account_number,
                'is_active': emp.is_active,
                'created_at': emp.created_at.isoformat()
            })
        
        return Response(employee_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load employees: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def departments_public(request):
    """
    Public departments endpoint for dashboard testing.
    No authentication required - returns department breakdown.
    """
    try:
        departments = PayrollEmployee.objects.values('role').annotate(
            employee_count=Count('id'),
            avg_salary=Avg('base_salary'),
            total_salary=Sum('base_salary')
        ).order_by('role')
        
        department_data = []
        for dept in departments:
            department_data.append({
                'department': dept['role'],
                'employee_count': dept['employee_count'],
                'avg_salary': float(dept['avg_salary']) if dept['avg_salary'] else 0,
                'total_salary': float(dept['total_salary']) if dept['total_salary'] else 0
            })
        
        return Response(department_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load departments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def dashboard_stats_public(request):
    """
    Public dashboard stats endpoint for testing.
    No authentication required - returns basic dashboard statistics.
    """
    try:
        total_employees = PayrollEmployee.objects.count()
        active_employees = PayrollEmployee.objects.filter(is_active=True).count()
        total_companies = Company.objects.count()
        total_salary = PayrollEmployee.objects.aggregate(
            total=Sum('base_salary')
        )['total'] or 0
        
        stats = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': total_employees - active_employees,
            'total_companies': total_companies,
            'total_monthly_salary': float(total_salary),
            'average_salary': float(total_salary / total_employees) if total_employees > 0 else 0
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to load dashboard stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =================================================================
# COMPANY MANAGEMENT VIEWSET (ADMIN ONLY)
# =================================================================
class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing companies
    Only Admin users can create, update, or delete companies
    All authenticated users can view companies they have access to
    
    Permissions:
    - Admin: Full CRUD access to all companies
    - HR/Director: Read-only access to their associated company
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        if self.request.user.extendeduser.is_admin():
            return Company.objects.all()
        return Company.objects.filter(id=self.request.user.extendeduser.company_id)


class ExtendedUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user roles.
    Only Admin users can manage user roles.
    """
    queryset = ExtendedUser.objects.all()
    serializer_class = ExtendedUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class PayrollEmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employees.
    HR can manage employees in their company.
    """
    queryset = PayrollEmployee.objects.all()
    serializer_class = PayrollEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsHR]

    def get_queryset(self):
        user = self.request.user
        if user.extendeduser.is_admin():
            return PayrollEmployee.objects.all()
        elif user.extendeduser.company:
            return PayrollEmployee.objects.filter(company=user.extendeduser.company)
        return PayrollEmployee.objects.none()

    def perform_create(self, serializer):
        # Automatically assign to HR's company if not admin
        if not self.request.user.extendeduser.is_admin() and self.request.user.extendeduser.company:
            serializer.save(company=self.request.user.extendeduser.company)
        else:
            serializer.save()


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payrolls.
    HR can create and manage payrolls.
    Director can approve payrolls.
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsHR]
        elif self.action in ['approve_payrolls', 'mark_as_paid']:
            permission_classes = [permissions.IsAuthenticated, IsDirector]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.extendeduser.is_admin():
            return Payroll.objects.all()
        elif user.extendeduser.company:
            return Payroll.objects.filter(employee__company=user.extendeduser.company)
        return Payroll.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsDirector])
    def approve_payrolls(self, request):
        """
        Approve multiple payrolls at once.
        Only Directors can approve payrolls.
        """
        serializer = PayrollApprovalSerializer(data=request.data)
        if serializer.is_valid():
            payroll_ids = serializer.validated_data['payroll_ids']
            payrolls = Payroll.objects.filter(
                id__in=payroll_ids,
                status='Pending',
                employee__company=request.user.extendeduser.company
            )
            
            approved_count = 0
            errors = []
            
            for payroll in payrolls:
                try:
                    if payroll.approve_payroll(request.user):
                        approved_count += 1
                except ValueError as e:
                    errors.append(f"Payroll {payroll.id}: {str(e)}")
            
            return Response({
                'approved_count': approved_count,
                'total_requested': len(payroll_ids),
                'errors': errors
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsDirector])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a single payroll as paid.
        Only Directors can mark payrolls as paid.
        """
        payroll = get_object_or_404(Payroll, pk=pk, employee__company=request.user.extendeduser.company)
        
        if payroll.mark_as_paid():
            return Response({'message': 'Payroll marked as paid successfully'})
        
        return Response(
            {'error': 'Payroll must be approved before marking as paid'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Get monthly payroll summary for the current month.
        """
        now = timezone.now()
        month = request.query_params.get('month', now.month)
        year = request.query_params.get('year', now.year)
        
        queryset = self.get_queryset().filter(month=month, year=year)
        
        summary = queryset.aggregate(
            total_payrolls=Count('id'),
            pending_count=Count('id', filter=Q(status='Pending')),
            approved_count=Count('id', filter=Q(status='Approved')),
            paid_count=Count('id', filter=Q(status='Paid')),
            total_amount=Sum('final_salary') or 0,
            pending_amount=Sum('final_salary', filter=Q(status='Pending')) or 0,
        )
        
        return Response(summary)


class PayrollNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payroll notifications.
    Employees can only see their own notifications.
    """
    queryset = PayrollNotification.objects.all()
    serializer_class = PayrollNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            employee = PayrollEmployee.objects.get(user=user)
            return PayrollNotification.objects.filter(employee=employee)
        except PayrollEmployee.DoesNotExist:
            return PayrollNotification.objects.none()

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = get_object_or_404(PayrollNotification, pk=pk, employee__user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the current user"""
        try:
            employee = PayrollEmployee.objects.get(user=request.user)
            updated = PayrollNotification.objects.filter(
                employee=employee, 
                is_read=False
            ).update(is_read=True)
            return Response({'message': f'{updated} notifications marked as read'})
        except PayrollEmployee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics based on user role.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get dashboard statistics based on user role.
        """
        user = request.user
        extended_user = user.extendeduser
        
        if extended_user.is_director():
            return self._director_stats(extended_user)
        elif extended_user.is_hr():
            return self._hr_stats(extended_user)
        elif extended_user.is_admin():
            return self._admin_stats()
        
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    def _director_stats(self, extended_user):
        """Statistics for Director users"""
        company = extended_user.company
        if not company:
            return Response({'error': 'No company assigned'}, status=status.HTTP_400_BAD_REQUEST)

        stats = {
            'total_employees': PayrollEmployee.objects.filter(company=company, is_active=True).count(),
            'pending_payrolls': Payroll.objects.filter(employee__company=company, status='Pending').count(),
            'approved_payrolls': Payroll.objects.filter(employee__company=company, status='Approved').count(),
            'paid_payrolls': Payroll.objects.filter(employee__company=company, status='Paid').count(),
            'total_payroll_amount': Payroll.objects.filter(
                employee__company=company, 
                status__in=['Approved', 'Paid']
            ).aggregate(total=Sum('final_salary'))['total'] or 0,
            'company_balance': company.bank_balance,
            'unread_notifications': 0  # Directors don't receive payroll notifications
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    def _hr_stats(self, extended_user):
        """Statistics for HR users"""
        company = extended_user.company
        if not company:
            return Response({'error': 'No company assigned'}, status=status.HTTP_400_BAD_REQUEST)

        current_month = timezone.now().month
        current_year = timezone.now().year

        stats = {
            'total_employees': PayrollEmployee.objects.filter(company=company, is_active=True).count(),
            'pending_payrolls': Payroll.objects.filter(
                employee__company=company, 
                status='Pending',
                month=current_month,
                year=current_year
            ).count(),
            'approved_payrolls': Payroll.objects.filter(
                employee__company=company, 
                status='Approved',
                month=current_month,
                year=current_year
            ).count(),
            'paid_payrolls': Payroll.objects.filter(
                employee__company=company, 
                status='Paid',
                month=current_month,
                year=current_year
            ).count(),
            'total_payroll_amount': Payroll.objects.filter(
                employee__company=company,
                month=current_month,
                year=current_year
            ).aggregate(total=Sum('final_salary'))['total'] or 0,
            'company_balance': company.bank_balance,
            'unread_notifications': 0  # HR doesn't receive employee notifications
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    def _admin_stats(self):
        """Statistics for Admin users"""
        stats = {
            'total_employees': PayrollEmployee.objects.filter(is_active=True).count(),
            'pending_payrolls': Payroll.objects.filter(status='Pending').count(),
            'approved_payrolls': Payroll.objects.filter(status='Approved').count(),
            'paid_payrolls': Payroll.objects.filter(status='Paid').count(),
            'total_payroll_amount': Payroll.objects.filter(
                status__in=['Approved', 'Paid']
            ).aggregate(total=Sum('final_salary'))['total'] or 0,
            'company_balance': Company.objects.aggregate(total=Sum('bank_balance'))['total'] or 0,
            'unread_notifications': 0  # Admins don't receive payroll notifications
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsDirector])
    def company_funds(self, request):
        """
        Get company funds overview for Directors.
        """
        company = request.user.extendeduser.company
        if not company:
            return Response({'error': 'No company assigned'}, status=status.HTTP_400_BAD_REQUEST)

        pending_amount = Payroll.objects.filter(
            employee__company=company,
            status='Pending'
        ).aggregate(total=Sum('final_salary'))['total'] or 0

        funds_data = {
            'company_name': company.name,
            'current_balance': company.bank_balance,
            'pending_payroll_amount': pending_amount,
            'remaining_after_payroll': company.bank_balance - pending_amount,
            'can_afford_pending': company.bank_balance >= pending_amount
        }

        serializer = CompanyFundsSerializer(funds_data)
        return Response(serializer.data)


# Employee Management ViewSet
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for managing employees with comprehensive database operations.
    HR and Admin can CRUD employees, Directors can only view.
    Includes search, filtering, and bulk operations.
    """
    queryset = PayrollEmployee.objects.select_related('user', 'company').all()
    serializer_class = PayrollEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter employees by company with optimized queries."""
        user = self.request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            queryset = PayrollEmployee.objects.select_related('user', 'company').filter(
                company=user.extendeduser.company
            )
            
            # Apply filters from query parameters
            search = self.request.query_params.get('search', None)
            department = self.request.query_params.get('department', None)
            status = self.request.query_params.get('status', None)
            
            if search:
                queryset = queryset.filter(
                    Q(user__first_names__icontains=search) |
                    Q(user__last_names__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(user__email__icontains=search) |
                    Q(role__icontains=search) |
                    Q(phone__icontains=search)
                )
            
            if department:
                queryset = queryset.filter(role__icontains=department)
            
            if status is not None:
                is_active = status.lower() == 'true'
                queryset = queryset.filter(is_active=is_active)
                
            return queryset.order_by('-created_at')
        
        return PayrollEmployee.objects.none()

    def get_permissions(self):
        """
        Set permissions based on action:
        - HR and Admin can create, update, delete
        - Director can only view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsHROrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated, IsAuthorizedUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Set company automatically when creating employee."""
        user = self.request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            serializer.save(company=user.extendeduser.company)
        else:
            raise serializers.ValidationError("User must be associated with a company")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsHROrAdmin])
    def deactivate(self, request, pk=None):
        """Deactivate an employee."""
        employee = self.get_object()
        employee.is_active = False
        employee.save()
        
        # Log the action
        logger.info(f"Employee {employee.user.username} deactivated by {request.user.username}")
        
        return Response({
            'message': 'Employee deactivated successfully',
            'employee_id': employee.id,
            'status': 'inactive'
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsHROrAdmin])
    def activate(self, request, pk=None):
        """Activate an employee."""
        employee = self.get_object()
        employee.is_active = True
        employee.save()
        
        # Log the action
        logger.info(f"Employee {employee.user.username} activated by {request.user.username}")
        
        return Response({
            'message': 'Employee activated successfully',
            'employee_id': employee.id,
            'status': 'active'
        })

    @action(detail=False, methods=['get'])
    def departments(self, request):
        """Get all departments with employee counts."""
        user = request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            departments = PayrollEmployee.objects.filter(
                company=user.extendeduser.company,
                is_active=True
            ).values('department').annotate(
                employee_count=Count('id')
            ).order_by('department')
            
            return Response(list(departments))
        return Response([])

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get employees grouped by department."""
        department = request.query_params.get('department')
        queryset = self.get_queryset().filter(is_active=True)
        
        if department:
            queryset = queryset.filter(department=department)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# User Management ViewSet
class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users and their roles.
    Only Admin can manage users.
    """
    queryset = ExtendedUser.objects.all()
    serializer_class = ExtendedUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        """Filter users by company."""
        user = self.request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            return ExtendedUser.objects.filter(company=user.extendeduser.company)
        return ExtendedUser.objects.none()

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change user role."""
        user_profile = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in ['Admin', 'HR', 'Director', 'Employee']:
            return Response(
                {'error': 'Invalid role'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile.role = new_role
        user_profile.save()
        
        return Response({'message': f'User role changed to {new_role}'})

    @action(detail=True, methods=['post'])
    def deactivate_user(self, request, pk=None):
        """Deactivate a user account."""
        user_profile = self.get_object()
        user_profile.user.is_active = False
        user_profile.user.save()
        return Response({'message': 'User account deactivated'})

    @action(detail=True, methods=['post'])
    def activate_user(self, request, pk=None):
        """Activate a user account."""
        user_profile = self.get_object()
        user_profile.user.is_active = True
        user_profile.user.save()
        return Response({'message': 'User account activated'})


# Analytics ViewSet
class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics and reporting.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorizedUser]

    @action(detail=False, methods=['get'])
    def payroll_trends(self, request):
        """Get payroll trends over time."""
        months = int(request.query_params.get('months', 6))
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=30 * months)

        trends = Payroll.objects.filter(
            created_at__gte=start_date,
            employee__company=request.user.extendeduser.company
        ).extra(
            select={'month': "strftime('%%Y-%%m', created_at)"}
        ).values('month').annotate(
            total_amount=Sum('final_salary'),
            count=Count('id'),
            avg_salary=Avg('final_salary')
        ).order_by('month')

        return Response(list(trends))

    @action(detail=False, methods=['get'])
    def department_costs(self, request):
        """Get cost breakdown by department."""
        department_costs = PayrollEmployee.objects.filter(
            company=request.user.extendeduser.company,
            is_active=True
        ).values('department').annotate(
            total_employees=Count('id'),
            total_salary_cost=Sum('basic_salary'),
            avg_salary=Avg('basic_salary')
        ).order_by('-total_salary_cost')

        return Response(list(department_costs))

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent payroll activity."""
        days = int(request.query_params.get('days', 7))
        since_date = timezone.now() - timezone.timedelta(days=days)

        recent_payrolls = Payroll.objects.filter(
            employee__company=request.user.extendeduser.company,
            created_at__gte=since_date
        ).select_related('employee').order_by('-created_at')[:20]

        activities = []
        for payroll in recent_payrolls:
            activities.append({
                'id': payroll.id,
                'employee_name': payroll.employee.name,
                'amount': float(payroll.final_salary),
                'status': payroll.status,
                'date': payroll.created_at,
                'type': 'payroll_created'
            })

        # Add notification activities
        recent_notifications = PayrollNotification.objects.filter(
            payroll__employee__company=request.user.extendeduser.company,
            created_at__gte=since_date
        ).select_related('payroll__employee').order_by('-created_at')[:10]

        for notification in recent_notifications:
            activities.append({
                'id': f"notification_{notification.id}",
                'employee_name': notification.payroll.employee.name,
                'message': notification.message,
                'date': notification.created_at,
                'type': 'notification'
            })

        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        serializer = RecentActivitySerializer(activities[:20], many=True)
        return Response(serializer.data)


# Company Profile ViewSet
class CompanyProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for managing company profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorizedUser]

    @action(detail=False, methods=['get'])
    def details(self, request):
        """Get company profile details."""
        user = request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            company = user.extendeduser.company
            
            # Get department statistics
            departments = PayrollEmployee.objects.filter(
                company=company,
                is_active=True
            ).values('department').annotate(
                employee_count=Count('id'),
                total_salary_cost=Sum('basic_salary'),
                avg_salary=Avg('basic_salary')
            ).order_by('department')

            company_data = {
                'id': company.id,
                'name': company.name,
                'bank_balance': company.bank_balance,
                'total_employees': PayrollEmployee.objects.filter(company=company, is_active=True).count(),
                'total_departments': departments.count(),
                'departments': list(departments)
            }

            serializer = CompanyProfileSerializer(company_data)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No company profile found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def update_balance(self, request):
        """Update company bank balance."""
        user = request.user
        if hasattr(user, 'extendeduser') and user.extendeduser.company:
            company = user.extendeduser.company
            new_balance = request.data.get('bank_balance')
            
            if new_balance is None:
                return Response(
                    {'error': 'Bank balance is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                company.bank_balance = float(new_balance)
                company.save()
                return Response({'message': 'Bank balance updated successfully'})
            except ValueError:
                return Response(
                    {'error': 'Invalid bank balance value'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'error': 'No company profile found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_auth_token(request):
    """
    Generate authentication token for user login.
    
    POST /api/auth/token/
    Body: {
        "username": "admin",
        "password": "admin123"
    }
    
    Returns: {
        "token": "abcd1234...",
        "user": {
            "id": 1,
            "username": "admin",
            "role": "Admin",
            "email": "admin@techcorp.com"
        }
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user role
        user_role = 'Employee'  # default
        if hasattr(user, 'extendeduser'):
            user_role = user.extendeduser.role
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user_role
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication])
def logout_user(request):
    """
    Logout user by deleting their authentication token.
    
    POST /api/auth/logout/
    Headers: Authorization: Token <token>
    
    Returns: {
        "message": "Successfully logged out"
    }
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response(
            {'error': 'Logout failed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication])
def verify_token(request):
    """
    Verify if the current token is valid and return user info.
    
    GET /api/auth/verify/
    Headers: Authorization: Token <token>
    
    Returns: {
        "valid": true,
        "user": {
            "id": 1,
            "username": "admin",
            "role": "Admin",
            "email": "admin@techcorp.com"
        }
    }
    """
    user_role = 'Employee'  # default
    if hasattr(request.user, 'extendeduser'):
        user_role = request.user.extendeduser.role
    
    return Response({
        'valid': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'role': user_role
        }
    })
