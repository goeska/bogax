from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0004_rename_legacy_bx_sales_tables"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Customer",
            new_name="Partner",
        ),
        migrations.AlterModelTable(
            name="partner",
            table="partner",
        ),
        migrations.RenameField(
            model_name="salesorder",
            old_name="customer",
            new_name="partner",
        ),
        migrations.AddField(
            model_name="partner",
            name="is_customer",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AddField(
            model_name="partner",
            name="is_vendor",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]

