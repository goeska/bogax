from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0006_rename_partner_id_sequence"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="is_active",
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]

