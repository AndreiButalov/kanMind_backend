from django.urls import path
from .views import TaskView, BoardView, BoardDetailView, TaskDetail

urlpatterns = [
    path('tasks/', TaskView.as_view()),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('boards/', BoardView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]
