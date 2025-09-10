from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'users', views.ExtendedUserViewSet)
router.register(r'employees', views.PayrollEmployeeViewSet)
router.register(r'payrolls', views.PayrollViewSet)
router.register(r'notifications', views.PayrollNotificationViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

# New comprehensive API endpoints
router.register(r'employee-management', views.EmployeeViewSet, basename='employee-management')
router.register(r'user-management', views.UserManagementViewSet, basename='user-management')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
router.register(r'company-profile', views.CompanyProfileViewSet, basename='company-profile')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Test database connection
    path('test-db/', views.test_db_connection, name='test-db'),
    
    # Public testing endpoints (no authentication required)
    path('test-db-public/', views.public_test_db_connection, name='test-db-public'),
    path('employees-public/', views.public_test_employees, name='employees-public'),
    path('departments-public/', views.public_test_departments, name='departments-public'),
    path('dashboard-stats-public/', views.public_dashboard_stats, name='dashboard-stats-public'),
    
    # Dashboard stats endpoint
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('company-profile-details/', views.company_profile, name='company-profile-details'),
    
    # Authentication endpoints
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/signup/', auth_views.signup_view, name='signup'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/profile/', auth_views.profile_view, name='profile'),
    
    # Token authentication endpoints
    path('auth/token/', views.get_auth_token, name='get-auth-token'),
    path('auth/logout-token/', views.logout_user, name='logout-token'),
    path('auth/verify/', views.verify_token, name='verify-token'),
    
    # API endpoints
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
