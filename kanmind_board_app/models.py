from django.db import models

class Board(models.Model):
    title = models.TextField(max_length=255)
    members = models.TextField(max_length=255)
    owner = models.TextField(max_length=255)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=100, blank=True)
    status = models.TextField(max_length=20, default='to_do')
    priority = models.TextField(max_length=20, blank=True)
    reviewer_id = models.TextField(max_length=20, blank=True)
    assignee_id = models.TextField(max_length=20, blank=True)
    due_date = models.DateField()
    board = models.TextField()


class Comment(models.Model):
    task = models.TextField()
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.TextField()