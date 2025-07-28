from .serializers import TaskSerializers, BoardSerializer, CommentSerializer, BoardDetailSerializer, TaskAssignedToMeSerializer, UserProfileSimpleSerializer, BoardCreateSerializer
from kanMind_app.models import Task, Board, Comment
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from user_auth_app.models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from .permissions import IsBoardMemberOrOwner, IsInSameBoardPermission, IsBoardMemberFromComment, CanCreateBoard
from django.db import models
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed

@api_view(['GET'])
def assigned_tasks(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "UserProfile not found"}, status=400)

    tasks = Task.objects.filter(assignee_id=user_profile).distinct()
    serializer = TaskAssignedToMeSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def reviewer_tasks(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "UserProfile not found"}, status=400)

    tasks = Task.objects.filter(reviewer_id=user_profile).distinct()
    serializer = TaskAssignedToMeSerializer(tasks, many=True)
    return Response(serializer.data)

class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    # permission_classes = [IsInSameBoardPermission]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({"detail": "UserProfile nicht gefunden."}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            board_id = request.data.get('board')
            if not board_id:
                return Response({"detail": "Board-ID ist erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return Response({"detail": "Board nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

            if user_profile != board.owner and user_profile not in board.members.all():
                return Response(
                    {"detail": "Du bist kein Mitglied dieses Boards."},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"Interner Serverfehler: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    

class TaskDetail(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInSameBoardPermission]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class BoardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanCreateBoard]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Board.objects.none()

        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user_profile)
        ).distinct()

    def get(self, request, *args, **kwargs):
        boards = self.get_queryset()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = BoardCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        title = serializer.validated_data.get('title')
        member_ids = serializer.validated_data.get('members', [])

        try:
            owner_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"detail": "UserProfile not found"}, status=status.HTTP_400_BAD_REQUEST)

        board = Board.objects.create(title=title, owner=request.user)
        board.members.add(owner_profile)

        invalid_ids = []
        for member_id in member_ids:
            if member_id == owner_profile.id:
                continue
            try:
                member = UserProfile.objects.get(pk=member_id)
                board.members.add(member)
            except UserProfile.DoesNotExist:
                invalid_ids.append(member_id)

        if invalid_ids:
            return Response(
                {"members": f"Invalid user profile IDs: {invalid_ids}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = BoardSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)



class BoardDetailView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBoardMemberOrOwner]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        board = self.get_object()
        data = request.data

        title = data.get('title')
        if title is not None:
            board.title = title

        members = data.get('members', None)
        if members is not None:
            new_members = UserProfile.objects.filter(id__in=members)
            board.members.set(new_members)

        board.save()

        try:
            owner_profile = UserProfile.objects.get(user=board.owner)
        except UserProfile.DoesNotExist:
            owner_profile = None

        response_data = {
            "id": board.id,
            "title": board.title,
            "owner_data": UserProfileSimpleSerializer(owner_profile).data if owner_profile else {},
            "members_data": UserProfileSimpleSerializer(board.members.all(), many=True).data
        }

        return Response(response_data)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class TaskCommentsView(APIView):

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        content = serializer.validated_data.get("content", "").strip()
        if not content:
            return Response({"detail": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"detail": "UserProfile nicht gefunden."}, status=status.HTTP_403_FORBIDDEN)

        board = task.board
        if not board or (user_profile != board.owner and user_profile not in board.members.all()):
            return Response({"detail": "Du bist kein Mitglied dieses Boards."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_auth, _ = TokenAuthentication().authenticate(request)
            if not user_auth or not user_auth.is_authenticated:
                raise NotAuthenticated()
        except AuthenticationFailed:
            return Response({"detail": "Ungültiger Token."}, status=status.HTTP_401_UNAUTHORIZED)
        except NotAuthenticated:
            return Response({"detail": "Nicht eingeloggt."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": f"Interner Serverfehler: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
        except Comment.DoesNotExist:
            return Response({"detail": "Kommentar nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response(
                {"detail": "Nur der Autor darf diesen Kommentar löschen."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user_authenticator = TokenAuthentication()
            user_auth, _ = user_authenticator.authenticate(request)
            if not user_auth or not user_auth.is_authenticated:
                raise NotAuthenticated("Nicht autorisiert.")
        except AuthenticationFailed:
            return Response({"detail": "Ungültiger Token."}, status=status.HTTP_401_UNAUTHORIZED)
        except NotAuthenticated:
            return Response({"detail": "Nicht eingeloggt."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": f"Interner Serverfehler: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return Response({"detail": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user__email=email)
            data = {
                "id": user_profile.id,
                "fullname": user_profile.user.username,
                "email": email,
            }
            return Response(data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Email not found"}, status=status.HTTP_404_NOT_FOUND)