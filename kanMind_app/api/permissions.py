from rest_framework import permissions
from user_auth_app.models import UserProfile

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
  
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return False

        return user_profile in obj.board.members.all()

    def has_permission(self, request, view):
        # Für ListView (kein einzelnes Objekt)
        if request.method in permissions.SAFE_METHODS:
            user = request.user
            if not user.is_authenticated:
                return False

            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                return False

            # Filterbare Querysets in der View, also hier True zurückgeben
            return True

        return True