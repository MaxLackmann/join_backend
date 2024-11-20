from django.db import migrations

def create_guest_user(apps, schema_editor):
    User = apps.get_model('join_app', 'User')
    if not User.objects.filter(id=0).exists():
        guest_user = User(
            id=0,
            username="Guest",
            email="guest@example.com",
            password="",
            emblem="G",  # Standardemblem für Guest
            color="#CCCCCC"  # Standardfarbe für Guest
        )
        guest_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0002_initial'),  # Ersetze 'previous_migration_file' durch die vorherige Migrationsdatei
    ]

    operations = [
        migrations.RunPython(create_guest_user),
    ]