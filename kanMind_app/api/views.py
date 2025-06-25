from .serializers import TaskSerializers, BoardSerializer
from kanMind_app.models import Task, Board
from rest_framework import mixins
from rest_framework import generics


class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskSerializers

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)  
      
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)



class BoardView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)  
      
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)