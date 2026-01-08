from kanmind_board_app.models import Board, Task, Comment
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics, status
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsTaskBoardMember, CanDeleteTask, IsCommentAuthor, IsTaskBoardMemberForComment, IsBoardMemberForCreation
from .serializers import (
    BoardSerializer, TaskSerializer, CommentSerializer, BoardDetailSerializer, BoardResponseSerializer,
    BoardUpdateSerializer, TaskDetailWithOutBoard, TaskSerializerWithOutBoard, TaskSingleSerializerPut,
)


class BoardsView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()    
    

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class BoardSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        return BoardResponseSerializer

    def get(self, request, *args, **kwargs):
        serializer = BoardDetailSerializer(self.get_object())
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = BoardUpdateSerializer(board, data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        response_serializer = BoardResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = BoardUpdateSerializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        response_serializer = BoardResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated, IsBoardOwner]
        self.check_permissions(request)
        return self.destroy(request, *args, **kwargs)





class TasksView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskSerializer
        return TaskDetailWithOutBoard

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board')

        if not board_id:
            return Response(
                {"detail": "Board-ID ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user
        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            return Response(
                {"detail": "Benutzer muss Mitglied des Boards sein."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        detail_serializer = TaskDetailWithOutBoard(task)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        


class TaskSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), CanDeleteTask()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskSerializerWithOutBoard
        return TaskDetailWithOutBoard

    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs.get('pk'))
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs.get('pk'))
        serializer = TaskSerializerWithOutBoard(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        response_serializer = TaskSingleSerializerPut(task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs.get('pk'))
        serializer = TaskSerializerWithOutBoard(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        response_serializer = TaskSingleSerializerPut(task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(id=kwargs.get('pk'))
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, task):
                return Response({"detail": "Nur der Ersteller der Task oder der Board-Eigentümer kann löschen."}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class CommentsView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=request.user,
            task_id=self.kwargs['task_id']
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    

class CommentsDeleteView(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response(
                {"detail": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.get_full_name() or user.username
            }
            return Response(data, status=status.HTTP_200_OK) 

        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        


class TasksAssignedToMeView(TasksView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee_id=user)


class TasksReviewingView(TasksView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer_id=user)