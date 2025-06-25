from .serializers import TaskSerializers
from kanMind_app.models import Task
from rest_framework import mixins
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskSerializers

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)  
      
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs) 