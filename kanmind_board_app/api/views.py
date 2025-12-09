from .serializers import BoardSerializer, TaskSerializer, CommentSerializer
from kanmind_board_app.models import Board, Task, Comment
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics, status


class BoardsView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

# @api_view(['GET', 'POST'])
# def boards_view(request):

#     if request.method == 'GET':
#         boards = Board.objects.all()
#         serializer = BoardSerializer(boards, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     if request.method == 'POST':
#         serializer = BoardSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class BoardSingleView(
            mixins.RetrieveModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin,
            generics.GenericAPIView,):
    
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)




# @api_view(['GET', 'DELETE', 'PUT'])
# def board_single_view(request, pk):

#     if request.method == 'GET':
#         board = Board.objects.get(pk=pk)
#         serializer = BoardSerializer(board)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     if request.method == 'DELETE':
#         board = Board.objects.get(pk=pk)
#         serializer = BoardSerializer(board)
#         board.delete()
#         return Response(serializer.data)
    
#     if request.method == 'PUT':
#         board = Board.objects.get(pk=pk)
#         serializer = BoardSerializer(board, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
def tasks_view(request):

    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


@api_view(['GET'])
def comments_view(request):

    if request.method == 'GET':
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)