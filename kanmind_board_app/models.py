from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.TextField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=100, blank=True)
    status = models.TextField(max_length=20, default='to_do')
    priority = models.TextField(max_length=20, blank=True)
    reviewer_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="review_tasks")
    assignee_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks")
    due_date = models.DateField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')


class Comment(models.Model):
    task = models.TextField()
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.TextField()