from django.db import models
from user_auth_app.models import UserProfile



class Comment(models.Model):
    pass


class Task(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    priority = models.CharField(max_length=20, default="medium")
    reviewer = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='task')
    due_date = models.DateField()
    comments = models.TextField()


class Board(models.Model):
    title = title = models.TextField(blank=True, null=True)
    member = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='board')


