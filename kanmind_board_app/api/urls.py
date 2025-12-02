from django.urls import path
from .views import board_view


urlpatterns = [
    path('boards/', board_view)
]
