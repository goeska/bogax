from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0009_sales_order_order_type_state_only"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="address",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]

