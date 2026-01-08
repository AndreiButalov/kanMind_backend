from kanmind_board_app.models import Board, Task, Comment
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import mixins, generics, status
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsTaskBoardMember, CanDeleteTask, IsCommentAuthor, IsTaskBoardMemberForComment
from .serializers import (
    BoardSerializer, TaskSerializer, TaskDetailSerializer, CommentSerializer, BoardDetailSerializer, BoardResponseSerializer,
    BoardUpdateSerializer, TaskDetailWithOutBoard, TaskSerializerWithOutBoard, TaskSingleSerializerPut,
)


class BoardsView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    """
    API-View für Listen und Erstellen von Boards.

    GET: Gibt alle Boards zurück, bei denen der Benutzer Eigentümer oder Mitglied ist.
    POST: Erstellt ein neues Board. Der aktuelle Benutzer wird automatisch als Mitglied hinzugefügt.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtert Boards für den aktuellen Benutzer.
        """
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
    """
    API-View für einzelne Boards.

    GET: Gibt die Board-Details zurück.
    PUT/PATCH: Aktualisiert das Board.
    DELETE: Löscht das Board (nur Eigentümer erlaubt).
    """
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    """Wählt den Serializer abhängig von der HTTP-Methode."""
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
    """
    API-View für Aufgaben.

    GET: Listet alle Tasks (optional Filter in Subclasses).
    POST: Erstellt eine neue Task in einem Board, überprüft, dass der Benutzer Mitglied ist.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    def get_serializer_class(self): 
        """Wählt Serializer abhängig von der HTTP-Methode."""       
        if self.request.method == 'POST':
            return TaskSerializer
        return TaskDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board')
        if not board_id:
            return Response(
                {"detail": "Board-ID ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )

        board = get_object_or_404(Board, id=board_id)

        user = request.user
        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            return Response(
                {"detail": "Benutzer muss Mitglied des Boards sein."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        
        return Response(
            TaskDetailSerializer(task).data,
            status=status.HTTP_201_CREATED
        )        


class TaskSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):  
    """
    API-View für einzelne Tasks.

    GET: Gibt Task-Details zurück.
    PATCH/PUT: Aktualisiert die Task (Board-ID kann nicht geändert werden).
    DELETE: Löscht die Task (nur Assignee, Reviewer oder Board-Eigentümer).
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_permissions(self):
        """Ersetzt Permissions für DELETE-Anfragen."""

        if self.request.method == 'DELETE':
            return [IsAuthenticated(), CanDeleteTask()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Wählt Serializer abhängig von der HTTP-Methode."""

        if self.request.method in ['PUT', 'PATCH']:
            return TaskSerializerWithOutBoard
        return TaskDetailWithOutBoard

    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs.get('pk'))
        serializer = self.get_serializer(task)
        return Response(serializer.data)   

    def patch(self, request, *args, **kwargs):
        """Teil-Update einer Task (Board-ID kann nicht geändert werden)."""

        if 'board' in request.data:
            return Response(
                {"detail": "Das Ändern der Board-ID ist nicht erlaubt."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            task = Task.objects.get(id=kwargs.get('pk'))
        except Task.DoesNotExist:
            return Response(
                {"detail": "Task nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, task)

        serializer = TaskSerializerWithOutBoard(
            task,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        response_serializer = TaskSingleSerializerPut(task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        """Löscht eine Task nach Berechtigungsprüfung."""
        
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
    """
    API-View für Kommentare zu einer Task.

    GET: Listet alle Kommentare einer Task.
    POST: Erstellt einen Kommentar, der automatisch den aktuellen Benutzer als Author setzt.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def get_task(self):
        """
        Holt die Task anhand von task_id.
        Prüft die Object Permissions für den Benutzer.
        """
        try:
            task = Task.objects.get(id=self.kwargs['task_id'])
        except Task.DoesNotExist:
            raise NotFound("Task nicht gefunden.")
        self.check_object_permissions(self.request, task)
        return task

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = self.get_task() 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, task=task)
        return Response(serializer.data, status=201)
    

class CommentsDeleteView(APIView):
    """
    API-View für das Löschen eines Kommentars.

    DELETE: Löscht einen Kommentar, nur Author erlaubt.
    """
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_object(self, task_id, pk):
        task = get_object_or_404(Task, id=task_id)

        comment = get_object_or_404(Comment, id=pk, task=task)

        self.check_object_permissions(self.request, comment)
        return comment

    def delete(self, request, task_id, pk):
        comment = self.get_object(task_id, pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class EmailCheckView(APIView):
    """
    API-View zum Überprüfen, ob eine Email existiert.

    GET: query parameter 'email' -> Gibt User-Daten zurück, falls vorhanden.
    """
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
    """
    API-View für Tasks, die dem aktuellen Benutzer zugewiesen sind.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtert Tasks, bei denen der aktuelle Benutzer Assignee ist."""
        user = self.request.user
        return Task.objects.filter(assignee_id=user)


class TasksReviewingView(TasksView):
    """
    API-View für Tasks, bei denen der aktuelle Benutzer als Reviewer eingetragen ist.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtert Tasks, bei denen der aktuelle Benutzer Reviewer ist."""
        user = self.request.user
        return Task.objects.filter(reviewer_id=user)