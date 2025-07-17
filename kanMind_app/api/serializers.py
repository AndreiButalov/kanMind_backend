from rest_framework import serializers
from kanMind_app.models import Task, Board, Comment
from user_auth_app.models import UserProfile

class UserProfileSimpleSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'fullname', 'email']


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']


class TaskSerializers(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        required=False,
        write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        required=False,
        write_only=True
    )

    assignee = serializers.SerializerMethodField(read_only=True)
    reviewer = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'reviewer_id', 'assignee_id', 'board', 'due_date',
            'assignee', 'reviewer', 'comments_count'
        ]

    def get_assignee(self, obj):
        assignee = obj.assignee_id.first()
        return UserProfileSimpleSerializer(assignee).data if assignee else None

    def get_reviewer(self, obj):
        reviewer = obj.reviewer_id.first()
        return UserProfileSimpleSerializer(reviewer).data if reviewer else None

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        assignee = validated_data.pop('assignee_id', None)
        reviewer = validated_data.pop('reviewer_id', None)
        task = Task.objects.create(**validated_data)

        if assignee:
            task.assignee_id.set([assignee])

        if reviewer:
            task.reviewer_id.set([reviewer])

        return task

    def update(self, instance, validated_data):
        assignee = validated_data.pop('assignee_id', None)
        reviewer = validated_data.pop('reviewer_id', None)

        if assignee is not None:
            instance.assignee_id.set([assignee])

        if reviewer is not None:
            instance.reviewer_id.set([reviewer])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


        

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count',
            'ticket_count', 'tasks_to_do_count',
            'tasks_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

# serializers.py

class TaskSimpleSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_assignee(self, obj):
        assignees = obj.assignee_id.all()
        return UserProfileSimpleSerializer(assignees[0]).data if assignees else None

    def get_reviewer(self, obj):
        reviewers = obj.reviewer_id.all()
        return UserProfileSimpleSerializer(reviewers[0]).data if reviewers else None

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskNestedSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_assignee(self, obj):
        assignees = obj.assignee_id.all()
        if assignees.exists():
            return UserProfileSimpleSerializer(assignees.first()).data
        return None

    def get_reviewer(self, obj):
        reviewers = obj.reviewer_id.all()
        if reviewers.exists():
            return UserProfileSimpleSerializer(reviewers.first()).data
        return None

    def get_comments_count(self, obj):
        return obj.comments.count()
    

class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserProfileSimpleSerializer(many=True, read_only=True)
    tasks = TaskNestedSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']



class TaskAssignedToMeSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]

    def get_assignee(self, obj):
        assignees = obj.assignee_id.all()
        if assignees:
            return UserProfileSimpleSerializer(assignees[0]).data
        return None

    def get_reviewer(self, obj):
        reviewers = obj.reviewer_id.all()
        if reviewers:
            return UserProfileSimpleSerializer(reviewers[0]).data
        return None
    

class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Board
        fields = ['title', 'members']