from django.db import models
from user_auth_app.models import UserProfile

class Task(models.Model):
    # board
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    priority = models.CharField(max_length=20, default="medium")
    reviewer = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    comments = models.TextField()

