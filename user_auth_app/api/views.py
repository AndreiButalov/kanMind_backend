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
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
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