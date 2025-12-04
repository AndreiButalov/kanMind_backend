from django.db import models

class Board(models.Model):
    title = models.TextField(max_length=255)
    members = models.TextField(max_length=255)
    owner = models.TextField(max_length=255)
