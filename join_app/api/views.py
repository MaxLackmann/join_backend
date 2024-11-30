from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from join_app.models import Contact, Task, User, Subtask, TaskContact
from join_app.api.serializers import ContactSerializer, TaskSerializer,\
    UserSerializer, SubtaskSerializer, TaskContactSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class TaskContactViewSet(viewsets.ViewSet):
    queryset = TaskContact.objects.all()
    serializer_class = TaskContactSerializer
    """
    Handles listing and retrieving task-specific contacts.
    """
    
    def create(self, request, task_id=None, *args, **kwargs):
        """Assign contacts with their checked status to the given task."""
        if not task_id:
            return Response({"error": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Hole den Task
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Verarbeite die übergebenen Kontakte und checked-Status
        task_contacts_data = request.data.get('task_contacts', [])
        task_contacts = []

        for task_contact_data in task_contacts_data:
            contact_id = task_contact_data.get('contact').get('id')
            checked = task_contact_data.get('checked', False)  # Standardwert: False
            try:
                contact = Contact.objects.get(pk=contact_id)
                task_contact, created = TaskContact.objects.get_or_create(
                    task=task,
                    contact=contact,
                    defaults={'checked': checked}
                )
                if not created:  # Falls bereits existiert, aktualisiere checked
                    task_contact.checked = checked
                    task_contact.save()
                task_contacts.append(task_contact)
            except Contact.DoesNotExist:
                return Response({"error": f"Contact with ID {contact_id} not found."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Serialisiere die aktualisierten Kontakte
        serializer = TaskContactSerializer(task_contacts, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, task_id=None, *args, **kwargs):
        """List all contacts associated with a specific task."""
        if not task_id:
            return Response({"error": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        task_contacts = TaskContact.objects.filter(task_id=task_id)
        serializer = TaskContactSerializer(task_contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, task_id=None, pk=None, *args, **kwargs):
        """Retrieve a specific contact associated with a task."""
        if not task_id or not pk:
            return Response({"error": "Task ID and Contact ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task_contact = TaskContact.objects.get(task_id=task_id, id=pk)
        except TaskContact.DoesNotExist:
            return Response({"error": "TaskContact not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskContactSerializer(task_contact)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def list(self, request, task_id=None, *args, **kwargs):
        if not task_id:
            return Response({"error": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
        task_contacts = TaskContact.objects.filter(task_id=task_id).select_related('contact', 'task')  # Verbundene Daten vorab laden
        serializer = TaskContactSerializer(task_contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, task_id=None, *args, **kwargs):
        """Create a subtask under the specified task."""
        data = request.data
        if task_id:
            data['task'] = task_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, task_id=None, pk=None, *args, **kwargs):
        """Retrieve a specific subtask."""
        try:
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, task_id=None, pk=None, *args, **kwargs):
        """Delete a subtask only if it belongs to the given task."""
        try:
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=status.HTTP_404_NOT_FOUND)

        subtask.delete()
        return Response({"message": "Subtask deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, task_id=None, pk=None, *args, **kwargs):
        """Update a subtask only if it belongs to the given task."""
        try:
            subtask = Subtask.objects.get(pk=pk, task_id=task_id)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found for this task."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(subtask, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            # Bearbeite die `task_contacts` separat
            task_contacts_data = request.data.pop('task_contacts', [])
            response = super().create(request, *args, **kwargs)
    
            # Erstelle TaskContacts nach der Task-Erstellung
            task_id = response.data['cardId']
            task = Task.objects.get(pk=task_id)
    
            for task_contact_data in task_contacts_data:
                contact_id = task_contact_data.get('contact').get('id')
                checked = task_contact_data.get('checked', False)
                contact = Contact.objects.get(pk=contact_id)
                TaskContact.objects.create(task=task, contact=contact, checked=checked)
    
            return response
        except ValidationError as e:
            print("Validation Error:", e.detail)
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Lade TaskContacts und ihre Kontakte
        task_contacts = TaskContact.objects.filter(task=instance).select_related('contact')
        task_contact_serializer = TaskContactSerializer(task_contacts, many=True)
        data['task_contacts'] = task_contact_serializer.data  # Vollständige Verschachtelung

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
    
        # Bearbeite `task_contacts` separat
        task_contacts_data = data.pop('task_contacts', None)
    
        # Aktualisiere die Task
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
    
        # Aktualisiere TaskContacts
        if task_contacts_data:
            for task_contact_data in task_contacts_data:
                contact_id = task_contact_data.get('contact').get('id')
                checked = task_contact_data.get('checked', False)
                contact = Contact.objects.get(pk=contact_id)
    
                task_contact, created = TaskContact.objects.update_or_create(
                    task=updated_instance,
                    contact=contact,
                    defaults={'checked': checked}
                )
    
        return Response(self.get_serializer(updated_instance).data, status=status.HTTP_200_OK)