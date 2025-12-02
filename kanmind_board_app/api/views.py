from .serializers import BoardSerializer
from kanmind_board_app.models import Board
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def board_view(request):
    if request.method == 'GET':
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)
