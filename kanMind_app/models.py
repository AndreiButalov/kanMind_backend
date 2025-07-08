from django.db import models
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User


class Board(models.Model):
    title = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(UserProfile, related_name='boards')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=4, related_name="owned_boards")

    def __str__(self):
        return self.title if self.title else f"Board #{self.id}"

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True, default='to_do')
    priority = models.CharField(max_length=20)       
    reviewer_id = models.ManyToManyField(UserProfile, blank=True, related_name='reviewer_tasks') 
    assignee_id = models.ManyToManyField(UserProfile, blank=True, related_name='assignee_tasks')           
    due_date = models.DateField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.title if self.title else f"Task #{self.id}"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        author_name = self.author.username if self.author else "Unknown"
        return f"{author_name}: {self.content[:20]}"

    class Meta:
        ordering = ['-created_at']
