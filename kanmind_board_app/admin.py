from django.contrib import admin
from .models import Board, Task, Comment

# class BoardAdmin(admin.ModelAdmin):
#     list_filter=['title']
#     # list_display=['title', 'members', 'owner']

admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Comment)
