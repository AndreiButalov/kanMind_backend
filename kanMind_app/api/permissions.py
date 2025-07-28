from rest_framework import permissions
from user_auth_app.models import UserProfile
from kanMind_app.models import Task, Board
from rest_framework.exceptions import NotFound

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
        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False

            try:
                board = Board.objects.get(id=board_id)
                user_profile = UserProfile.objects.get(user=request.user)
                return user_profile == board.owner or user_profile in board.members.all()
            except (Board.DoesNotExist, UserProfile.DoesNotExist):
                return False

        return True  # Für andere Methoden wie GET etc.

    def has_object_permission(self, request, view, obj):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return False

        if hasattr(obj, 'board') and obj.board:
            return user_profile == obj.board.owner or user_profile in obj.board.members.all()

        return False


    

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
    """
    Erlaubt das Erstellen von Boards nur für authentifizierte Benutzer mit einem gültigen UserProfile.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            UserProfile.objects.get(user=request.user)
            return True
        except UserProfile.DoesNotExist:
            return False
        
