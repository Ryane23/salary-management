from django.db import models
import employee

# Create your models here.
class Contract(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE)
    contract_type = models.CharField(max_length=50, blank=False, null=False)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    taxes_deductions = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    CNPS_deductions = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)


    def __str__(self):
        return f"{self.employee.user.first_names} {self.employee.user.last_names} - {self.contract_type}"
    