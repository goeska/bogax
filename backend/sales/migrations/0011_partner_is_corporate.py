from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0010_partner_address"),
    ]

    operations = [
        # Column `partner.is_corporate` already exists in the existing database.
        # Register it in Django's migration state without altering the DB.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="partner",
                    name="is_corporate",
                    field=models.BooleanField(db_index=True, default=False),
                ),
            ],
        )
    ]

