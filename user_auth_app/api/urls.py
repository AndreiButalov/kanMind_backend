from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegisrationView, LoginView

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegisrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login')
]