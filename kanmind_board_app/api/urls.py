from django.urls import path
from .views import boards_view, board_single_view, tasks_view, comments_view


urlpatterns = [
    path('boards/', boards_view),
    path('boards/<int:pk>/', board_single_view),
    path('tasks/', tasks_view),
    path('comments/', comments_view),
]
