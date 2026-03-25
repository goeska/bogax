from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("purchase", "0003_purchaseorder_state_received"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_receiving_order_code "
                "ON receiving_order (code);"
            ),
            reverse_sql="DROP INDEX IF EXISTS idx_receiving_order_code;",
        ),
    ]
