from rest_framework import serializers
from kanmind_board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    members = serializers.CharField(max_length=255)
    owner = serializers.CharField(max_length=255)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner']

    def create(self, validated_data):
        return Board.objects.create(**validated_data)