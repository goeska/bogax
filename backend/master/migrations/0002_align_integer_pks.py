# PK types in PostgreSQL are integer (serial); sync migration state so dependent
# apps (e.g. sales) generate integer FK columns. No database_operations — tables
# stay maintained outside Django / unchanged here.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="productcategory",
                    name="id",
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="product",
                    name="id",
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="tablenumber",
                    name="id",
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="tax",
                    name="id",
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="uom",
                    name="id",
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
            ],
            database_operations=[],
        ),
    ]
