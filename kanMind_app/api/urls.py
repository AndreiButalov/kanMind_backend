from django.urls import path
from .views import TaskView, BoardView

urlpatterns = [
    path('tasks/', TaskView.as_view()),
    path('boards/', BoardView.as_view()),
]
