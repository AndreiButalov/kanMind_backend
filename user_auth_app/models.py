from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """
    Model für zusätzliche Informationen zu einem User.

    Felder:
    - user: OneToOneField auf das User-Objekt. Jede User-Instanz kann genau ein UserProfile haben.
    
    Methoden:
    - __str__: Gibt den Username des zugehörigen Users zurück.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        """
        Rückgabe des Usernamens des zugehörigen Users.
        """
        return self.user.username
