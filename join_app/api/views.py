from rest_framework import viewsets
from rest_framework.response import Response
from join_app.models import Contact, Task, User, Subtask, TaskUser
from join_app.api.serializers import ContactSerializer, TaskSerializer, UserSerializer, SubtaskSerializer, TaskUserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def list(self, request, task_id=None, *args, **kwargs):
        """Filter subtasks by the task_id provided in the URL."""
        if task_id:
            subtasks = Subtask.objects.filter(task_id=task_id)
        else:
            subtasks = Subtask.objects.all()
        serializer = self.get_serializer(subtasks, many=True)
        return Response(serializer.data)

    def create(self, request, task_id=None, *args, **kwargs):
        """Create a subtask under the specified task."""
        data = request.data
        if task_id:
            data['task'] = task_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def retrieve(self, request, task_id=None, pk=None, *args, **kwargs):
        """Einen spezifischen Subtask im Kontext einer Aufgabe abrufen."""
        try:
            # Sicherstellen, dass der Subtask zur Aufgabe gehört
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=404)

        serializer = self.get_serializer(subtask)
        return Response(serializer.data)
    
    def destroy(self, request, task_id=None, pk=None, *args, **kwargs):
        """Lösche einen Subtask nur, wenn er zur angegebenen Aufgabe gehört."""
        try:
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=404)

        subtask.delete()
        return Response({"message": "Subtask deleted successfully."}, status=204)
    
    def update(self, request, task_id=None, pk=None, *args, **kwargs):
        """Aktualisiere einen Subtask nur, wenn er zur angegebenen Aufgabe gehört."""
        try:
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=404)

        serializer = self.get_serializer(subtask, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def retrieve(self, request, *args, **kwargs):
        """Task-Daten abrufen, inklusive TaskUser und Subtasks."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        task_users = TaskUser.objects.filter(task=instance)
        task_user_serializer = TaskUserSerializer(task_users, many=True)
        data['task_users'] = task_user_serializer.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
    
        # Separate task_users aus dem Rest der Daten
        task_users_data = data.pop('task_users', None)
    
        # Aktualisiere den Task
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
    
        # Aktualisiere die Many-to-Many-Relation task_users
        if task_users_data is not None:
            updated_instance.task_users.set(task_users_data)
    
        return Response(self.get_serializer(updated_instance).data)