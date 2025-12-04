from rest_framework import serializers
from kanmind_board_app.models import Board

class BoardSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Board
        fields = '__all__'

    
    
    