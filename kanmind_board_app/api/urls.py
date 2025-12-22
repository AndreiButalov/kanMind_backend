from django.urls import path
from .views import BoardsView, BoardSingleView, TasksView, EmailCheckView, TaskSingleView, CommentsView, CommentsDeleteView, TasksAssignedToMeView, TasksReviewingView


urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-detail'),
    path('tasks/', TasksView.as_view()),
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view()),
    path('tasks/reviewing/', TasksReviewingView.as_view()),
    path('tasks/<int:pk>/', TaskSingleView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentsView.as_view()),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentsDeleteView.as_view(), name='comment-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
