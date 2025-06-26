from django.urls import path
from .views import TaskView, BoardView, BoardDetailView

urlpatterns = [
    path('tasks/', TaskView.as_view()),
    path('boards/', BoardView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]
