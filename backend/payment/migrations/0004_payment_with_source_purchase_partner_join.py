from django.db import migrations


VIEW_SQL = """
CREATE OR REPLACE VIEW payment_with_source AS
SELECT
    p.id,
    p.tx_type,
    p.source_table,
    p.source_pk,
    p.reference_code,
    p.amount,
    p.currency_code,
    p.transaction_at,
    p.note,
    p.created_by_id,
    COALESCE(u.email, '') AS created_by_email,
    p.is_active,
    p.created_at,
    p.updated_at,
    CASE
        WHEN p.source_table = 'sales_order' THEN so.id
        WHEN p.source_table = 'purchase_order' THEN po.id
        ELSE NULL
    END AS source_id,
    CASE
        WHEN p.source_table = 'sales_order' THEN COALESCE(so.code, '')
        WHEN p.source_table = 'purchase_order' THEN COALESCE(po.code, '')
        ELSE COALESCE(p.reference_code, '')
    END AS source_code,
    CASE
        WHEN p.source_table = 'sales_order' THEN COALESCE(so.state, '')
        WHEN p.source_table = 'purchase_order' THEN COALESCE(po.state, '')
        ELSE ''
    END AS source_state,
    CASE
        WHEN p.source_table = 'sales_order' THEN so.time_transaction
        WHEN p.source_table = 'purchase_order' THEN po.time_transaction
        ELSE p.transaction_at
    END AS source_transaction_at,
    CASE
        WHEN p.source_table = 'sales_order' THEN COALESCE(prs.name, '')
        WHEN p.source_table = 'purchase_order' THEN COALESCE(prp.name, '')
        ELSE ''
    END AS source_party_name,
    CASE
        WHEN p.source_table = 'sales_order' THEN COALESCE(prs.phone, '')
        WHEN p.source_table = 'purchase_order' THEN COALESCE(prp.phone, '')
        ELSE ''
    END AS source_party_phone
FROM payment p
LEFT JOIN accounts_user u ON u.id = p.created_by_id
LEFT JOIN sales_order so ON p.source_table = 'sales_order' AND so.id = p.source_pk
LEFT JOIN partner prs ON prs.id = so.partner_id
LEFT JOIN purchase_order po ON p.source_table = 'purchase_order' AND po.id = p.source_pk
LEFT JOIN partner prp ON prp.id = po.partner_id;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0003_payment_with_source_partner_join"),
        ("purchase", "0002_purchase_order_partner_fk"),
    ]

    operations = [
        migrations.RunSQL(
            sql=VIEW_SQL,
            reverse_sql="DROP VIEW IF EXISTS payment_with_source;",
        ),
    ]

