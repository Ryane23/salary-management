# Payroll Management System

A comprehensive Django-based payroll management system with role-based access control, automatic salary calculations, and notification features.

## Features

### 1. **User Roles & Permissions**
- **Admin**: Manage users, companies, and system-wide settings
- **HR**: Manage employees, attendance, and create payrolls
- **Director**: Approve payrolls, view company funds, and manage salary distribution

### 2. **Core Models**

#### Company
- Company information and bank balance management
- Track company funds for payroll distribution
- Automatic balance deduction upon payroll approval

#### PayrollEmployee
- Extended employee model with payroll-specific information
- Base salary, bank details, and role information
- Company association for multi-company support

#### Payroll
- Monthly payroll processing with automatic salary calculation
- Formula: `final_salary = base_salary + bonus - deductions`
- Status tracking: Pending → Approved → Paid
- Attendance days, bonuses, and deductions management

#### PayrollNotification
- Automatic notifications for payroll status changes
- SMS and email integration support
- Read/unread status tracking

### 3. **Business Logic**

#### HR Workflow
1. Create/import employee data
2. Enter attendance, bonuses, and deductions
3. Set payment dates
4. Submit payrolls for approval

#### Director Workflow
1. Review pending payrolls
2. Check company funds availability
3. Approve payrolls (automatically deducts from company balance)
4. Mark payrolls as paid
5. Monitor company financial status

#### Automatic Processes
- Final salary calculation on payroll save
- Company balance validation before approval
- Notification generation on status changes
- Email/SMS sending (configurable)

### 4. **API Endpoints**

#### Authentication Required for All Endpoints

```
/payroll/api/companies/                 # Admin only
/payroll/api/users/                     # Admin only
/payroll/api/employees/                 # HR access
/payroll/api/payrolls/                  # HR create, Director approve
/payroll/api/notifications/             # Employee own data
/payroll/api/dashboard/stats/           # Role-based dashboard
/payroll/api/dashboard/company_funds/   # Director only
```

#### Key API Features
- Role-based filtering and permissions
- Batch payroll approval
- Monthly summaries and reports
- Company financial overview
- Notification management

### 5. **Management Commands**

```bash
# Create monthly payrolls for all active employees
python manage.py create_monthly_payrolls --month 1 --year 2024

# Update company bank balance
python manage.py update_company_balance --company "Company Name" --amount 50000
```

### 6. **Signals & Notifications**

- Automatic notification creation on payroll approval
- Email notifications (configurable)
- SMS notifications (with service integration)
- Extended user creation on user registration

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Migration
```bash
python manage.py makemigrations payslip_reportcard
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Configure Settings
Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    'payslip_reportcard',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Email configuration (optional)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
```

## Usage Examples

### 1. Create a Company
```python
from payslip_reportcard.models import Company, ExtendedUser

# Admin creates company
company = Company.objects.create(
    name="Tech Corp",
    bank_balance=500000.00,
    created_by=admin_user
)
```

### 2. Add Employees
```python
from payslip_reportcard.models import PayrollEmployee

employee = PayrollEmployee.objects.create(
    user=user_instance,
    company=company,
    phone="+1234567890",
    role="Software Developer",
    base_salary=5000.00,
    bank_name="Bank ABC",
    bank_account_number="123456789"
)
```

### 3. Create Monthly Payroll
```python
from payslip_reportcard.models import Payroll

payroll = Payroll.objects.create(
    employee=employee,
    attendance_days=22,
    bonus=500.00,
    deductions=100.00,
    month=1,
    year=2024,
    created_by=hr_user
)
# final_salary is automatically calculated
```

### 4. Approve Payroll (Director)
```python
# Director approves payroll
result = payroll.approve_payroll(director_user)
if result:
    print("Payroll approved and company balance updated")
else:
    print("Insufficient company funds")
```

## API Usage Examples

### 1. Get Dashboard Stats
```bash
curl -H "Authorization: Token your-token" \
     http://localhost:8000/payroll/api/dashboard/stats/
```

### 2. Approve Multiple Payrolls
```bash
curl -X POST \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{"payroll_ids": [1, 2, 3]}' \
     http://localhost:8000/payroll/api/payrolls/approve_payrolls/
```

### 3. Get Company Funds Overview
```bash
curl -H "Authorization: Token your-token" \
     http://localhost:8000/payroll/api/dashboard/company_funds/
```

## Testing

Run the test suite:
```bash
python manage.py test payslip_reportcard
```

## Security Features

- Role-based access control
- Company-based data isolation
- Permission checks on all endpoints
- Automatic signal handlers for data integrity
- Validation for financial operations

## Extensibility

The system is designed to be modular and extensible:

1. **Custom Permissions**: Add new permission classes in `permissions.py`
2. **Additional Models**: Extend the system with new models
3. **Custom Signals**: Add business logic through Django signals
4. **API Extensions**: Create custom viewsets and endpoints
5. **Notification Channels**: Integrate additional notification services

## Best Practices

1. Always use transactions for financial operations
2. Validate company funds before payroll approval
3. Implement proper error handling in API calls
4. Use pagination for large datasets
5. Regular backup of financial data
6. Monitor notification delivery status
7. Implement audit logging for financial transactions

## Production Considerations

1. Use environment variables for sensitive settings
2. Configure proper email/SMS services
3. Set up monitoring and logging
4. Implement data backup strategies
5. Use HTTPS for all communications
6. Regular security audits
7. Database optimization for large datasets

## Support

For issues and questions:
1. Check the test files for usage examples
2. Review the API documentation
3. Examine the utility functions in `utils.py`
4. Test with management commands

---

**Note**: This system is designed to work within the existing Django project structure. Make sure to properly configure Django REST Framework and install all required dependencies before use.
