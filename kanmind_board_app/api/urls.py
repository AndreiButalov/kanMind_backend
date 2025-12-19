from django.urls import path
from .views import comments_view, BoardsView, BoardSingleView, TasksView, EmailCheckView, TaskSingleView


urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-detail'),
    path('tasks/', TasksView.as_view()),
    path('tasks/<int:pk>/', TaskSingleView.as_view(), name='task-detail'),
    path('comments/', comments_view),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
