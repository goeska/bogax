from django.db import migrations, models


def forwards_role_administrator(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role="admin").update(role="administrator")


def backwards_role_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role="administrator").update(role="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards_role_administrator, backwards_role_admin),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("administrator", "Administrator"),
                    ("manager", "Manager"),
                    ("staff", "Staff"),
                ],
                db_index=True,
                default="staff",
                max_length=20,
            ),
        ),
    ]
