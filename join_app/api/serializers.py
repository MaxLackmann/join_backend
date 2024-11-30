from rest_framework import serializers
from join_app.models import Contact, Task, User, TaskContact, Subtask

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Nur für Eingabe
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'emblem', 'color']
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'color', 'emblem',]

class TaskContactSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()  # Liefert alle Kontakt-Daten
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)

    class Meta:
        model = TaskContact
        fields = ['id', 'task', 'checked', 'contact']

    def get_filtered_contacts(self, obj):
        contacts = obj.task_contacts.filter(checked=True)
        return TaskContactSerializer(contacts, many=True).data

class SubtaskSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)  # Task ist optional

    class Meta:
        model = Subtask
        fields = ['id', 'task', 'subtaskText', 'checked']

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.filter(checked=True)
        return SubtaskSerializer(subtasks, many=True).data
    
class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, required=False)  # Subtasks inline
    task_contacts = TaskContactSerializer(many=True, required=False)  # Kontakte inline
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = Task
        fields = [
            'cardId', 'title', 'description', 'date', 
            'priority', 'category', 'subtasks', 'status', 'task_contacts'
        ]

    def create(self, validated_data):
        task_contacts_data = validated_data.pop('task_contacts', [])
        subtasks_data = validated_data.pop('subtasks', [])
        task = Task.objects.create(**validated_data)

        # Verarbeitung der TaskContacts
        for task_contact_data in task_contacts_data:
            contact_data = task_contact_data.get('contact')
            checked = task_contact_data.get('checked', False)  # Standardwert für checked
            if not contact_data:
                raise serializers.ValidationError(
                    {"task_contacts": "Each task_contact must include a contact object."}
                )
            contact = Contact.objects.get(id=contact_data['id'])
            TaskContact.objects.create(task=task, contact=contact, checked=checked)

        # Verarbeitung der Subtasks
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)

        return task

    def update(self, instance, validated_data):
        task_contacts_data = validated_data.pop('task_contacts', [])
        subtasks_data = validated_data.pop('subtasks', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    
        # Verarbeite TaskContacts
        for task_contact_data in task_contacts_data:
            task_contact_id = task_contact_data.get('id')
            contact_data = task_contact_data.get('contact')
            checked = task_contact_data.get('checked', False)  # Standardwert
            contact = Contact.objects.get(id=contact_data['id'])
    
            if task_contact_id:
                task_contact = TaskContact.objects.get(id=task_contact_id)
                task_contact.checked = checked
                task_contact.save()
            else:
                TaskContact.objects.create(task=instance, contact=contact, checked=checked)
    
        return instance