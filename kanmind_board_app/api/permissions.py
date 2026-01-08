from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):   
    """
    Permission, die sicherstellt, dass der Benutzer entweder der Eigentümer
    eines Boards ist oder Mitglied des Boards ist.

    Objektbasierte Berechtigung:
    - Zugriff wird erlaubt, wenn `obj.owner` der aktuelle Benutzer ist
    - oder wenn der Benutzer in `obj.members` enthalten ist
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(id=user.id).exists()


class IsBoardOwner(BasePermission): 
    """
    Permission, die nur dem Eigentümer eines Boards Zugriff erlaubt.

    Objektbasierte Berechtigung:
    - Zugriff wird nur erlaubt, wenn `obj.owner` der aktuelle Benutzer ist
    """
        
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    

class IsTaskBoardMember(BasePermission):
    """
    Permission für Aufgaben, die überprüft, ob der Benutzer Mitglied des zugehörigen Boards ist.

    Objektbasierte Berechtigung:
    - Zugriff wird erlaubt, wenn der Benutzer Eigentümer des Boards ist
    - oder wenn der Benutzer Mitglied des Boards ist (`board.members`)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(id=user.id).exists()    
    

class CanDeleteTask(BasePermission):
    """
    Permission, die steuert, wer eine Aufgabe löschen darf.

    Objektbasierte Berechtigung:
    - Zugriff wird erlaubt, wenn der Benutzer Eigentümer des Boards ist
    - oder wenn der Benutzer entweder Assignee (`obj.assignee_id`) oder Reviewer (`obj.reviewer_id`) der Aufgabe ist
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.board.owner == user:
            return True
        return obj.assignee_id == user or obj.reviewer_id == user
    


class IsTaskBoardMemberForComment(BasePermission):
    """
    Permission, die überprüft, ob ein Benutzer Kommentare zu einer Aufgabe sehen oder erstellen darf.

    Objektbasierte Berechtigung:
    - Zugriff wird erlaubt, wenn der Benutzer Eigentümer des Boards ist
    - oder wenn der Benutzer Mitglied des Boards ist (`board.members`)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(id=user.id).exists()


class IsCommentAuthor(BasePermission):
    """
    Permission, die sicherstellt, dass nur der Autor eines Kommentars Zugriff hat.

    Objektbasierte Berechtigung:
    - Zugriff wird nur erlaubt, wenn `obj.author` dem aktuellen Benutzer entspricht
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user   
