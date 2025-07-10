from rest_framework import permissions
from kanMind_app.models import Board
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

