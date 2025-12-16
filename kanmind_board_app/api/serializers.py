from rest_framework import serializers
from kanmind_board_app.models import Board, Task, Comment
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    member_count = serializers.SerializerMethodField()
    class Meta:
        model = Board
        fields = ['id', 'members', 'title', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()

    

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'