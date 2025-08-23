from django.db import models
import Dashboard

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey('Dashboard.User', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}: {self.message[:50]}..."