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

    def to_internal_value(self, data):
        if data.get('assignee_id') is None:
            data['assignee_id'] = []
        elif not isinstance(data['assignee_id'], list):
            data['assignee_id'] = [data['assignee_id']]

        if data.get('reviewer_id') is None:
            data['reviewer_id'] = []
        elif not isinstance(data['reviewer_id'], list):
            data['reviewer_id'] = [data['reviewer_id']]

        return super().to_internal_value(data)
    

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
    members = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        many=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    tasks = TaskSerializers(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'members',       
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'tasks',
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to_do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def to_representation(self, instance):        
        ret = super().to_representation(instance)
        ret['members'] = UserProfileSimpleSerializer(instance.members.all(), many=True).data
        return ret

