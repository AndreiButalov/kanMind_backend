from django.db import models
from user_auth_app.models import UserProfile



class Comment(models.Model):
    pass






class Board(models.Model):
    title = title = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(UserProfile, blank=True, related_name='board')

    def __str__(self):
        return self.title if self.title else f"Board #{self.id}"

class Task(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    priority = models.CharField(max_length=20)
    reviewer_id = models.TextField(blank=True, null=True)
    # assignee_id = models.ManyToManyField(UserProfile, blank=True, related_name='tasks')
    assignee_id = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    # comments = models.TextField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.title if self.title else f"Task #{self.id}"