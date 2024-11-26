from django.db import models

# Create your models here.

class User (models.Model):
    id = models.AutoField(primary_key=True)  # Standardmäßig primärer Schlüssel
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True)
    emblem = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.username

class Contact (models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    color = models.CharField(max_length=7, blank=True, null=True)
    emblem = models.CharField(max_length=10, blank=True, null=True) 
    
    def __str__(self):
        return self.name
    
class Task(models.Model):
    cardId = models.AutoField(primary_key=True)  # Automatisch nicht null
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    priority = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class TaskUser(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tasks")
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"

class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    subtaskText = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.subtaskText

