from django.urls import path
from .views import tasks_view, comments_view, BoardsView, BoardSingleView, TasksView


urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-detail'),
    # path('tasks/', tasks_view),
    path('tasks/', TasksView.as_view()),
    path('comments/', comments_view),
]
