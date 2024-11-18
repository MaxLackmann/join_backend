from rest_framework import viewsets
from join_app.models import Contact, Task, User
from join_app.api.serializers import ContactSerializer, TaskSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        """Fügt sicherheitshalber den Gastbenutzer hinzu, falls er nicht existiert."""
        User.objects.get_or_create(
            username="guest",
            defaults={"email": "guest@example.com", "password": ""}
        )
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        """Behandle Gastbenutzer-Abfrage separat."""
        if kwargs.get("pk") == "guest":
            guest_user, created = User.objects.get_or_create(
                username="guest",
                defaults={"email": "guest@example.com", "password": ""}
            )
            serializer = self.get_serializer(guest_user)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer