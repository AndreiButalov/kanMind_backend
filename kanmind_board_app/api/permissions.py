from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanmind_board_app.models import Task

class IsBoardMemberOrOwner(BasePermission):   
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(id=user.id).exists()


class IsBoardOwner(BasePermission):    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    

class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(id=user.id).exists()    
    

class CanDeleteTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.board.owner == user:
            return True
        return obj.assignee_id == user or obj.reviewer_id == user
    

class IsTaskBoardMemberForComment(BasePermission):
   def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False
        user = request.user
        board = task.board

        return board.owner == user or board.members.filter(id=user.id).exists()


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user