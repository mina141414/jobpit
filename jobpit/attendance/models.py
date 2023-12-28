from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Attendances(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attendance_time = models.DateTimeField(default=datetime.now)
    leave_time = models.DateTimeField(null=True)

