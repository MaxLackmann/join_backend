# Generated by Django 5.1.3 on 2024-11-24 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0004_remove_task_userid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='subtask',
        ),
    ]
