from django.urls import path
from .views import UsersView, UsersDetail


urlpatterns = [    
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:pk>/', UsersDetail.as_view(), name='users-detail'),
]