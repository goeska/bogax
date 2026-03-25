from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("purchase", "0002_purchase_order_partner_fk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="purchaseorder",
            name="state",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("confirmed", "Confirmed"),
                    ("received", "Received"),
                    ("void", "Void"),
                ],
                db_index=True,
                default="draft",
                max_length=20,
            ),
        ),
    ]
