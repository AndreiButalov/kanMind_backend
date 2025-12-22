from rest_framework import serializers
from kanmind_board_app.models import Board, Task, Comment
from django.contrib.auth.models import User


class UserSerialiser(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'fullname'
        ]

    def get_fullname(self, obj):
        full_name = obj.get_full_name().strip()
        return full_name if full_name else obj.username
        

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'members', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        user = self.context['request'].user

        board = Board.objects.create(
            owner=user,
            **validated_data
        )

        if user not in members:
            members.append(user)

        board.members.set(members)
        return board
    

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    

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


class TaskSerializerWithOutBoard(TaskSerializer, serializers.ModelSerializer):
    class Meta:
            model = Task
            fields = [
                'title', 'description', 'status', 'priority',
                'assignee_id', 'reviewer_id', 'due_date'
            ]



class TaskDetailSerializer(serializers.ModelSerializer):  
    assignee = UserSerialiser(source='assignee_id', read_only=True)
    reviewer = UserSerialiser(source='reviewer_id', read_only=True)
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer','due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()



class TaskDetailWithOutBoard(TaskDetailSerializer, serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerialiser(many=True, read_only=True)
    tasks = TaskDetailWithOutBoard(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id', 'members', 'tasks'
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance



class BoardResponseSerializer(serializers.ModelSerializer):
    owner_data = UserSerialiser(source='owner', read_only=True)
    members_data = UserSerialiser(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']



class CommentSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.id')
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']