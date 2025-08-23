from django.db import models
import employee

# Create your models here.
class attendance(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    status = models.CharField(max_length=20, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('mission_leave', 'mission_leave')], default='Present')

    def __str__(self):
        return f"{self.employee.user.first_names} {self.employee.user.last_names} - {self.date.strftime('%Y-%m-%d')} - {self.status}"
    
