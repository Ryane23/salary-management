from django.db import models
import employee

# Create your models here.
class Payslip(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE)
    month = models.DateField(auto_now_add=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    bank_name = models.CharField(max_length=100, blank=False, null=False)
    bank_account_number = models.CharField(max_length=20, blank=False, null=False)
    attendance_deductions = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return f"{self.employee.user.first_names} {self.employee.user.last_names} - {self.month.strftime('%B %Y')}"
    
