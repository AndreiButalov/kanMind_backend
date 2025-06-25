from django.urls import path
from .views import UsersView, UsersDetail, LoginView, RegisterView


urlpatterns = [    
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegisterView.as_view(), name='register'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:pk>/', UsersDetail.as_view(), name='users-detail'),
]