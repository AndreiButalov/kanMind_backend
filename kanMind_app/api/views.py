from .serializers import TaskSerializers, BoardSerializer, CommentSerializer, BoardDetailSerializer, TaskAssignedToMeSerializer, UserProfileSimpleSerializer, BoardCreateSerializer
from kanMind_app.models import Task, Board, Comment
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from user_auth_app.models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from .permissions import IsBoardMemberOrOwner, IsInSameBoardPermission, IsBoardMemberViaTask, IsCommentAuthor, IsBoardMemberFromComment, CanCreateBoard
from django.db import models
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsInSameBoardPermission]
    queryset = Task.objects.all()
    serializer_class = TaskSerializers

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

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
    permission_classes = [CanCreateBoard]
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBoardMemberViaTask]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden"}, status=404)

        comments = task.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden"}, status=404)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    

class DeleteCommentView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsCommentAuthor]
    queryset = Comment.objects.all()
    lookup_field = 'id'


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