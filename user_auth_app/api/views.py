from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins
from django.contrib.auth import authenticate
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token


class UsersView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UsersDetail(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'ok': False, 'status': 404, 'error': 'E-Mail nicht gefunden'}, status=404)

        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'fullname': user.username
            }, status=200)

        return Response({'ok': False, 'status': 401, 'error': 'Falsches Passwort'}, status=401)


class RegisterView(APIView):
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
            return Response({
                'ok': False,
                'status': 400,
                'errors': serializer.errors
            }, status=400)

