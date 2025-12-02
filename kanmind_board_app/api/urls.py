from django.urls import path
from .views import boards_view, board_single_view


urlpatterns = [
    path('boards/', boards_view),
    path('boards/<int:pk>/', board_single_view)
]
