from .serializers import BoardSerializer, TaskSerializer, CommentSerializer, BoardDetailSerializer, TaskDetailSerializer, TaskDetailWithOutBoard, TaskSerializerWithOutBoard
from kanmind_board_app.models import Board, Task, Comment
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics, status
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


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
    generics.GenericAPIView
):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskSerializer
        return TaskDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        detail_serializer = TaskDetailSerializer(task)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    


class TaskSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskSerializerWithOutBoard
        return TaskDetailWithOutBoard

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



@api_view(['GET'])
def comments_view(request):

    if request.method == 'GET':
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response({"detail": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user__email=email)
            data = {
                "id": user.id,
                "email": email,
                "fullname": user.username
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Email not found"}, status=status.HTTP_404_NOT_FOUND)