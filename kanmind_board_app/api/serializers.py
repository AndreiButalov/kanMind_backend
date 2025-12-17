from rest_framework import serializers
from kanmind_board_app.models import Board, Task, Comment
from django.contrib.auth.models import User


class UserSerialiser(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        full_name = obj.get_full_name().strip()
        return full_name if full_name else obj.username
        

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    member_count = serializers.SerializerMethodField()
    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerialiser(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
    

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'