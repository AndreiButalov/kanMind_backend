from rest_framework import serializers
from kanMind_app.models import Task, Board


class TaskSerializers(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'


class BoardSerializer(serializers.ModelSerializer):

    class Mate:
        model = Board
        fields = '__all__'