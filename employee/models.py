from django.db import models

import Dashboard

# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField('Dashboard.User', on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=False, null=False)
    department = models.CharField(max_length=100, blank=False, null=False)
    date_of_hire = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.first_names} {self.user.last_names} - {self.position}"
    