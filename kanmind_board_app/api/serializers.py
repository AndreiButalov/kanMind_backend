from rest_framework import serializers
from kanmind_board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    id = serializers.ImageField(read_only=True)
    title = serializers.CharField()
    members = serializers.CharField()
    owner = serializers.CharField()