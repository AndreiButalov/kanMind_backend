from .serializers import BoardSerializer, TaskSerializer, CommentSerializer, BoardDetailSerializer
from kanmind_board_app.models import Board, Task, Comment
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics, status


class BoardsView(
            mixins.ListModelMixin, 
            mixins.CreateModelMixin, 
            generics.GenericAPIView):
            
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BoardSingleView(
            mixins.RetrieveModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin,
            generics.GenericAPIView,):
    
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class TasksView(
            mixins.ListModelMixin, 
            mixins.CreateModelMixin, 
            generics.GenericAPIView):
            
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
    

