from rest_framework.permissions import BasePermission, SAFE_METHODS

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
    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(id=user.id).exists()


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user   
