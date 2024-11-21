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
    
class Task (models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    userId = models.ManyToManyField(User, blank=True)
    date = models.DateField()
    priority = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=100)
    subtask = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=100)
    cardId = models.IntegerField(unique=True, blank=True, null=True)
        
    def __str__(self):
        return self.title