from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_names = models.CharField(max_length=45, blank=False, null=False)
    last_names = models.CharField(max_length=45, blank=False, null=False)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, blank=False, null=False)

    def __str__(self):
        return self.username
    




