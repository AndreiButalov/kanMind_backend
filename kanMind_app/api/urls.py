from django.urls import path
from .views import TaskView, BoardView, BoardDetailView, TaskDetail, TaskCommentsView, DeleteCommentView, EmailCheckView


urlpatterns = [
    path('tasks/', TaskView.as_view()),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('boards/', BoardView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:id>/', DeleteCommentView.as_view(), name='delete-comment'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
