from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.TextField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=100, blank=True)
    status = models.TextField(max_length=20, default='to-do')
    priority = models.TextField(max_length=20, blank=True)
    reviewer_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="review_tasks")
    assignee_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks")
    due_date = models.DateField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """
        Rückgabe einer kurzen Darstellung des Kommentars:
        '<author>: <erste 20 Zeichen des Inhalts>'.
        """
        
        author_name = self.author.username if self.author else "Unknown"
        return f"{author_name}: {self.content[:20]}"

    class Meta:
        ordering = ['-created_at']