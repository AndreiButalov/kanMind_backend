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
    

class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'due_date'
        ]

class TaskDetailSerializer(serializers.ModelSerializer):  
    assignee = UserSerialiser(source='assignee_id', read_only=True)
    reviewer = UserSerialiser(source='reviewer_id', read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority','reviewer' ,'assignee','due_date']


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerialiser(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'tasks']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'