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
        many=True,
        required=False,
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        many=True,
        required=False,
    )

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'reviewer_id', 'assignee_id', 'due_date', 'board',
            'comments',
        ]


    # def to_internal_value(self, data):
    #     data = data.copy()

    #     for key in ['assignee_id', 'reviewer_id']:
    #         value = data.get(key)
    #         if value is not None and not isinstance(value, list):
    #             data[key] = [value]

    #     return super().to_internal_value(data)

    def update(self, instance, validated_data):
        if 'assignee_id' in validated_data:
            instance.assignee_id.set(validated_data.pop('assignee_id'))

        if 'reviewer_id' in validated_data:
            instance.reviewer_id.set(validated_data.pop('reviewer_id'))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        assignees = instance.assignee_id.all()
        ret['assignee'] = UserProfileSimpleSerializer(assignees[0]).data if assignees else None

        reviewer = instance.reviewer_id.all()
        ret['reviewer'] = UserProfileSimpleSerializer(reviewer[0]).data if reviewer else None
        ret['reviewer_id'] = UserProfileSimpleSerializer(reviewer, many=True).data
        ret['assignee_id'] = UserProfileSimpleSerializer(assignees, many=True).data

        ret['comments_count'] = instance.comments.count()
        return ret

        

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        many=True,
        required=False,
        allow_empty=True  # wichtig!
    )

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'members', 'member_count',
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