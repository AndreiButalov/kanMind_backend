from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für UserProfile-Objekte.

    Felder:
    - id: ID des zugehörigen Users (read-only)
    - fullname: Username des Users (read-only)
    - email: Email des Users (read-only)
    """
    id = serializers.IntegerField(source='user.id', read_only=True)
    fullname = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'fullname', 'email']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer für die Benutzerregistrierung.

    Felder:
    - fullname: Gewünschter Username (write-only)
    - email: Email-Adresse des Users
    - password: Passwort (write-only)
    - repeated_password: Passwort zur Bestätigung (write-only)

    Validierung:
    - Prüft, ob die Email bereits existiert.
    - Prüft, ob Passwort und repeated_password übereinstimmen.

    save():
    - Erstellt einen neuen User und ein zugehöriges UserProfile.
    - Speichert das Passwort sicher mit set_password().
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """
        Validiert, dass die Email-Adresse noch nicht verwendet wird.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return value

    def save(self):
        """
        Erstellt einen neuen User mit dem validierten Passwort und ein zugehöriges UserProfile.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'password': 'Passwörter stimmen nicht überein.'})
        
        user = User(
            username=self.validated_data['fullname'],
            email=self.validated_data['email'],
        )
        user.set_password(pw)
        user.save()
        
        UserProfile.objects.create(user=user)

        return user
