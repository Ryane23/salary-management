from django.contrib import admin
from .models import (
    Company, ExtendedUser, PayrollEmployee, 
    Payroll, PayrollNotification, Payslip_Reportcard
)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'bank_balance', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ExtendedUser)
class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'company', 'created_at']
    list_filter = ['role', 'company']
    search_fields = ['user__username', 'user__first_names', 'user__last_names']

@admin.register(PayrollEmployee)
class PayrollEmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'role', 'base_salary', 'is_active']
    list_filter = ['company', 'role', 'is_active']
    search_fields = ['user__first_names', 'user__last_names', 'role']
    readonly_fields = ['created_at']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'month', 'year', 'final_salary', 
        'status', 'payment_date', 'created_at'
    ]
    list_filter = ['status', 'month', 'year', 'employee__company']
    search_fields = [
        'employee__user__first_names', 
        'employee__user__last_names'
    ]
    readonly_fields = ['final_salary', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee__user', 'employee__company')

@admin.register(PayrollNotification)
class PayrollNotificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'message_preview', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['employee__user__first_names', 'employee__user__last_names', 'message']
    readonly_fields = ['sent_at']

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

@admin.register(Payslip_Reportcard)
class PayslipReportcardAdmin(admin.ModelAdmin):
    list_display = ['payslip', 'month', 'year']
    list_filter = ['month', 'year']
