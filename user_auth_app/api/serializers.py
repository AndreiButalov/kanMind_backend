from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    fullname = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'fullname', 'email', 'password', 'repeated_password']

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwörter stimmen nicht überein.'})
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')

        user = User(username=user_data['username'], email=user_data['email'])
        user.set_password(password)
        user.save()

        profile = UserProfile.objects.create(user=user)
        return profile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return value

    def save(self):
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
