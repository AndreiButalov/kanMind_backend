from rest_framework import permissions
from user_auth_app.models import UserProfile
from kanMind_app.models import Task, Board
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, NotFound, ParseError

class IsBoardMemberOrOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if obj.owner == user:
            return True

        try:
            user_profile = UserProfile.objects.get(user=user)
            return user_profile in obj.members.all()
        except UserProfile.DoesNotExist:
            return False


class IsInSameBoardPermission(permissions.BasePermission):
  
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return False

        if not hasattr(obj, 'board') or obj.board is None:
            return False

        return user_profile == obj.board.owner or user_profile in obj.board.members.all()

    

class IsBoardMemberFromComment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return NotFound("Comment not found.")

        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return NotFound("Comment not found.")

        task = getattr(obj, 'task', None)
        if not task:
            return NotFound("Comment not found.")

        board = task.board
        if profile == board.owner or profile in board.members.all():
            return True

        raise NotFound("Comment not found.")
    

class CanCreateBoard(permissions.BasePermission):
  
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            UserProfile.objects.get(user=request.user)
            return True
        except UserProfile.DoesNotExist:
            return False
        

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if obj.author != request.user:
            raise PermissionDenied("Du darfst nur deine eigenen Kommentare löschen.")
        return True
    

class IsBoardMemberViaTask(BasePermission):

    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        if not task_id:
            return False

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise PermissionDenied("Task nicht gefunden")

        board = task.board
        if not board:
            raise PermissionDenied("Task gehört zu keinem Board.")

        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Nicht authentifiziert oder kein Mitglied des Boards.")

        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("Kein gültiges UserProfile gefunden.")

        if board.owner == profile or profile in board.members.all():
            return True

        raise PermissionDenied("Du bist kein Mitglied dieses Boards.")
    


class CanCreateTaskOnBoard(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Nicht autorisiert. Der Benutzer muss eingeloggt sein.")

        board_id = request.data.get('board')
        if not board_id:
            raise ParseError("Ungültige Anfragedaten. 'board' Feld fehlt.")

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board nicht gefunden. Die angegebene Board-ID existiert nicht.")

        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("Kein gültiges UserProfile gefunden.")

        if board.owner == profile or profile in board.members.all():
            return True

        raise PermissionDenied("Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen.")