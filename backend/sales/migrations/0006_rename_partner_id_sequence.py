from django.db import migrations


RENAME_SEQ_SQL = """
DO $$
BEGIN
    IF to_regclass('public.customer_id_seq') IS NOT NULL
       AND to_regclass('public.partner_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE public.customer_id_seq RENAME TO partner_id_seq';
    END IF;
END $$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0005_partner_and_sales_order_fk"),
    ]

    operations = [
        migrations.RunSQL(
            sql=RENAME_SEQ_SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

