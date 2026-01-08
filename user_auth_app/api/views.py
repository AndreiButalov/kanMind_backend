from rest_framework import generics
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserProfileList(generics.ListCreateAPIView):
    """
    API-View zum Auflisten und Erstellen von UserProfiles.

    GET: Gibt alle UserProfiles zurück.
    POST: Erstellt ein neues UserProfile (über Serializer).
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API-View für einzelne UserProfiles.

    GET: Gibt Details eines UserProfiles zurück.
    PUT/PATCH: Aktualisiert das UserProfile.
    DELETE: Löscht das UserProfile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    """
    API-View für die Benutzerregistrierung.

    POST: Registriert einen neuen User, erstellt ein zugehöriges UserProfile
    und gibt einen Auth-Token zurück.
    
    Registriert einen neuen Benutzer.

    Validiert Daten über RegistrationSerializer.
    - Bei Erfolg: User und UserProfile erstellen, Token generieren, Daten zurückgeben.
    - Bei Fehler: Validierungsfehler zurückgeben.
        
    """
    permission_classes = [AllowAny]

    def post(self, request):        
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, _ = Token.objects.get_or_create(user=saved_account)
            return Response({
                'token': token.key,
                'user_id': saved_account.id,
                'email': saved_account.email,
                'fullname': saved_account.username
            }, status=201)
        else:
            return Response(serializer.errors, status=400)
    

class LoginView(APIView):
    """
    API-View für Benutzer-Login.

    POST: Authentifiziert einen Benutzer anhand von Email und Passwort.
    - Bei Erfolg: Gibt Auth-Token, user_id, Email und Username zurück.
    - Bei Fehler: Fehlermeldung zurückgeben (E-Mail nicht gefunden oder falsches Passwort).
    
    Authentifiziert Benutzer und erstellt einen Token.

    Schritte:
    1. User anhand der Email suchen.
    2. Passwort prüfen mit authenticate().
    3. Token erstellen oder abrufen.
    4. Erfolgs- oder Fehlerantwort zurückgeben.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'ok': False, 'error': 'E-Mail nicht gefunden'}, status=400)

        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'fullname': user.username
            }, status=200)

        return Response({'ok': False, 'error': 'Falsches Passwort'}, status=400)