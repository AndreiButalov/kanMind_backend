from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsBoardMemberOrOwner(BasePermission):
    """
    Zugriff nur, wenn User Owner oder Member des Boards ist
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(id=user.id).exists()
