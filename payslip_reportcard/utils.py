from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from .models import Company, PayrollEmployee, Payroll, PayrollNotification

class PayrollUtils:
    """Utility functions for payroll management"""
    
    @staticmethod
    def calculate_monthly_payroll_total(company, month, year):
        """Calculate total payroll amount for a company in a specific month/year"""
        return Payroll.objects.filter(
            employee__company=company,
            month=month,
            year=year
        ).aggregate(total=Sum('final_salary'))['total'] or Decimal('0.00')
    
    @staticmethod
    def get_company_payroll_summary(company):
        """Get comprehensive payroll summary for a company"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        return {
            'company_name': company.name,
            'bank_balance': company.bank_balance,
            'active_employees': PayrollEmployee.objects.filter(
                company=company, 
                is_active=True
            ).count(),
            'current_month_payrolls': Payroll.objects.filter(
                employee__company=company,
                month=current_month,
                year=current_year
            ).aggregate(
                total=Count('id'),
                pending=Count('id', filter=Q(status='Pending')),
                approved=Count('id', filter=Q(status='Approved')),
                paid=Count('id', filter=Q(status='Paid')),
                total_amount=Sum('final_salary')
            )
        }
    
    @staticmethod
    def can_afford_payroll_batch(company, payroll_ids):
        """Check if company can afford a batch of payrolls"""
        total_amount = Payroll.objects.filter(
            id__in=payroll_ids,
            status='Pending'
        ).aggregate(total=Sum('final_salary'))['total'] or Decimal('0.00')
        
        return company.bank_balance >= total_amount, total_amount
    
    @staticmethod
    def get_employee_payroll_history(employee, limit=12):
        """Get payroll history for an employee"""
        return Payroll.objects.filter(
            employee=employee
        ).order_by('-year', '-month')[:limit]
    
    @staticmethod
    def generate_payroll_report(company, month, year):
        """Generate detailed payroll report for a company"""
        payrolls = Payroll.objects.filter(
            employee__company=company,
            month=month,
            year=year
        ).select_related('employee__user')
        
        summary = payrolls.aggregate(
            total_employees=Count('id'),
            total_amount=Sum('final_salary') or Decimal('0.00'),
            pending_count=Count('id', filter=Q(status='Pending')),
            approved_count=Count('id', filter=Q(status='Approved')),
            paid_count=Count('id', filter=Q(status='Paid')),
            total_bonuses=Sum('bonus') or Decimal('0.00'),
            total_deductions=Sum('deductions') or Decimal('0.00'),
        )
        
        return {
            'company': company.name,
            'month': month,
            'year': year,
            'payrolls': list(payrolls.values(
                'employee__user__first_names',
                'employee__user__last_names',
                'employee__role',
                'employee__base_salary',
                'bonus',
                'deductions',
                'final_salary',
                'status',
                'payment_date'
            )),
            'summary': summary
        }

class NotificationUtils:
    """Utility functions for notifications"""
    
    @staticmethod
    def create_bulk_notifications(employees, message, payroll=None):
        """Create notifications for multiple employees"""
        notifications = []
        for employee in employees:
            notifications.append(
                PayrollNotification(
                    employee=employee,
                    message=message,
                    payroll=payroll
                )
            )
        
        return PayrollNotification.objects.bulk_create(notifications)
    
    @staticmethod
    def mark_notifications_read(employee, notification_ids=None):
        """Mark notifications as read for an employee"""
        queryset = PayrollNotification.objects.filter(employee=employee, is_read=False)
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        return queryset.update(is_read=True)
    
    @staticmethod
    def get_unread_count(employee):
        """Get count of unread notifications for an employee"""
        return PayrollNotification.objects.filter(
            employee=employee,
            is_read=False
        ).count()

class ReportUtils:
    """Utility functions for generating reports"""
    
    @staticmethod
    def generate_company_financial_summary(company):
        """Generate financial summary for a company"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Current month data
        current_payrolls = Payroll.objects.filter(
            employee__company=company,
            month=current_month,
            year=current_year
        )
        
        # Year-to-date data
        ytd_payrolls = Payroll.objects.filter(
            employee__company=company,
            year=current_year
        )
        
        return {
            'company_name': company.name,
            'current_balance': company.bank_balance,
            'current_month': {
                'month': current_month,
                'year': current_year,
                'total_payrolls': current_payrolls.count(),
                'total_amount': current_payrolls.aggregate(
                    total=Sum('final_salary')
                )['total'] or Decimal('0.00'),
                'status_breakdown': current_payrolls.values('status').annotate(
                    count=Count('id'),
                    amount=Sum('final_salary')
                )
            },
            'year_to_date': {
                'year': current_year,
                'total_payrolls': ytd_payrolls.count(),
                'total_amount': ytd_payrolls.aggregate(
                    total=Sum('final_salary')
                )['total'] or Decimal('0.00'),
                'monthly_breakdown': ytd_payrolls.values('month').annotate(
                    count=Count('id'),
                    amount=Sum('final_salary')
                ).order_by('month')
            }
        }
    
    @staticmethod
    def generate_employee_summary_report(company):
        """Generate employee summary report for a company"""
        employees = PayrollEmployee.objects.filter(
            company=company,
            is_active=True
        ).select_related('user')
        
        employee_data = []
        for employee in employees:
            recent_payroll = Payroll.objects.filter(
                employee=employee
            ).order_by('-year', '-month').first()
            
            employee_data.append({
                'name': employee.full_name,
                'role': employee.role,
                'base_salary': employee.base_salary,
                'last_payroll': {
                    'month': recent_payroll.month if recent_payroll else None,
                    'year': recent_payroll.year if recent_payroll else None,
                    'final_salary': recent_payroll.final_salary if recent_payroll else None,
                    'status': recent_payroll.status if recent_payroll else None,
                } if recent_payroll else None
            })
        
        return {
            'company_name': company.name,
            'total_employees': len(employee_data),
            'employees': employee_data
        }
