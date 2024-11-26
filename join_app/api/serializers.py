from rest_framework import serializers
from join_app.models import Contact, Task, User, TaskUser, Subtask

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Nur für Eingabe
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'emblem', 'color']
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'color', 'emblem']

class TaskUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = TaskUser
        fields = ['id', 'user', 'checked']

    def get_task_users(self, obj):
        subtasks = obj.task_users.filter(checked=True)
        return SubtaskSerializer(subtasks, many=True).data

class SubtaskSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False)  # Task ist optional

    class Meta:
        model = Subtask
        fields = ['id', 'task', 'subtaskText', 'checked']

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.filter(checked=True)
        return SubtaskSerializer(subtasks, many=True).data
    
class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, required=False)  # Verschachtelte Subtask-Daten
    task_users = TaskUserSerializer(many=True, required=False)  # Verschachtelte TaskUser-Daten    

    class Meta:
        model = Task
        fields = [
            'cardId', 'title', 'description', 'date', 
            'priority', 'category', 'subtasks', 'status', 'task_users'
        ]
        
    def create(self, validated_data):
        # Subtasks und Task-Users extrahieren
        task_users_data = validated_data.pop('task_users', [])
        subtasks_data = validated_data.pop('subtasks', [])
        
        # Task erstellen
        task = Task.objects.create(**validated_data)
    
        # Subtasks erstellen und mit dem Task verknüpfen
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)
    
        # TaskUsers erstellen und mit dem Task verknüpfen
        for task_user_data in task_users_data:
            TaskUser.objects.create(task=task, **task_user_data)
    
        return task
    
    def update(self, instance, validated_data):
        # Subtasks extrahieren
        subtasks_data = validated_data.pop('subtasks', [])
    
        # Aktualisieren der einfachen Felder des Tasks
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    
        # Verarbeiten der Subtasks
        existing_subtasks = {subtask.id: subtask for subtask in instance.subtasks.all()}
        sent_subtask_ids = {item.get('id') for item in subtasks_data if item.get('id')}
    
        # Löschen von Subtasks, die nicht mehr in den neuen Daten enthalten sind
        for subtask_id in existing_subtasks.keys() - sent_subtask_ids:
            existing_subtasks[subtask_id].delete()
    
        # Subtasks erstellen oder aktualisieren
        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id')
            if subtask_id and subtask_id in existing_subtasks:
                # Vorhandenen Subtask aktualisieren
                subtask = existing_subtasks[subtask_id]
                subtask.subtaskText = subtask_data.get('subtaskText', subtask.subtaskText)
                subtask.checked = subtask_data.get('checked', subtask.checked)
                subtask.save()
            else:
                # Entferne redundantes 'task'-Feld, falls vorhanden
                subtask_data.pop('task', None)
                # Neuen Subtask erstellen
                Subtask.objects.create(task=instance, **subtask_data)
    
        return instance