from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0012_project_table_and_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="salesorder",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="sales_orders",
                to="sales.project",
            ),
        ),
    ]
