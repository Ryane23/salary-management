from django.db import models
import payslip_reportcard

# Create your models here.
class Batch_payment(models.Model):
    Payslip_Reportcard = models.ForeignKey('payslip_reportcard.Payslip_Reportcard', on_delete=models.PROTECT)
    status=models.CharField(max_length=10, choices=[('valid', 'valid'), ('Pending', 'Pending'),  ('Cancelled', 'Cancelled')])
    day=models.DateField(auto_now_add=True)

    def __str__(self):
        payslip_reportcard_details = "\n".join([str(prc) for prc in payslip_reportcard.Payslip_Reportcard.objects.all()])
        return f"{payslip_reportcard_details}\n{self.status} - {self.day}"