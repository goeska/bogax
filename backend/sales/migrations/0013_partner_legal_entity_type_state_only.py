from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("master", "0009_legal_entity_type_state_only"),
        ("sales", "0012_project_table_and_state"),
    ]

    operations = [
        # Column `partner.legal_entity_type_id` already exists in the existing database.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="partner",
                    name="legal_entity_type",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="partners",
                        to="master.legalentitytype",
                        db_column="legal_entity_type_id",
                    ),
                )
            ],
        )
    ]

