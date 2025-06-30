from rest_framework import serializers
from kanMind_app.models import Task, Board, Comment



class CommentSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']


class TaskSerializers(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'reviewer_id', 'assignee_id', 'due_date', 'board',
            'comments',
        ]



class BoardSerializer(serializers.ModelSerializer):
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


