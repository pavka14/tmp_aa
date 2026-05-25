from django.contrib.auth.hashers import make_password
from django.db import migrations



def create_admin_superuser(apps, schema_editor):
    user_model = apps.get_model("auth", "User")
    user_model.objects.update_or_create(
        username="admin",
        defaults={
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "password": make_password("admin123"),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("infrastructure", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin_superuser, migrations.RunPython.noop),
    ]
