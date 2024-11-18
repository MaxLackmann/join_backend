from django.db import models

# Create your models here.

class User (models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username

class Contact (models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
class Task (models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    category = models.CharField(max_length=100)
    subtask = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title