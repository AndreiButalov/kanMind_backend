from django.db import models

class Board(models.Model):
    title = models.TextField()
    members = models.TextField()
    owner =models.TextField()
