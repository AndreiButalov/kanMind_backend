from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.TextField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')
    owner = models.TextField(max_length=255)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=100, blank=True)
    status = models.TextField(max_length=20, default='to_do')
    priority = models.TextField(max_length=20, blank=True)
    reviewer_id = models.ManyToManyField(User, blank=True, related_name='reviewer_tasks')
    assignee_id = models.ManyToManyField(User, blank=True, related_name='assignee_tasks')
    due_date = models.DateField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks'
    )


class Comment(models.Model):
    task = models.TextField()
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.TextField()