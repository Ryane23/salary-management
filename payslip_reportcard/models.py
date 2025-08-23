from django.db import models
import payslip

# Create your models here.
class Payslip_Reportcard(models.Model):
    payslip = models.ForeignKey('payslip.Payslip', on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(choices=[(i, f"{i:02d}") for i in range(1, 13)], blank=False, null=False)
    year = models.PositiveSmallIntegerField(blank=False, null=False)

    def __str__(self):
        return f"{self.month:02d}/{self.year} - {self.payslip}"
