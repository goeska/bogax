from django.db import migrations


RENAME_SQL = r"""
DO $$
BEGIN
    -- Rename tables only when legacy source exists and target does not.
    IF to_regclass('public.bx_sales_order_line_tax') IS NOT NULL
       AND to_regclass('public.sales_order_line_tax') IS NULL THEN
        EXECUTE 'ALTER TABLE public.bx_sales_order_line_tax RENAME TO sales_order_line_tax';
    END IF;

    IF to_regclass('public.bx_sales_order_line') IS NOT NULL
       AND to_regclass('public.sales_order_line') IS NULL THEN
        EXECUTE 'ALTER TABLE public.bx_sales_order_line RENAME TO sales_order_line';
    END IF;

    IF to_regclass('public.bx_sales_order') IS NOT NULL
       AND to_regclass('public.sales_order') IS NULL THEN
        EXECUTE 'ALTER TABLE public.bx_sales_order RENAME TO sales_order';
    END IF;

    IF to_regclass('public.bx_customer') IS NOT NULL
       AND to_regclass('public.customer') IS NULL THEN
        EXECUTE 'ALTER TABLE public.bx_customer RENAME TO customer';
    END IF;

    -- Rename common PK sequences created by serial/identity.
    IF to_regclass('public.bx_customer_id_seq') IS NOT NULL
       AND to_regclass('public.customer_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE public.bx_customer_id_seq RENAME TO customer_id_seq';
    END IF;
    IF to_regclass('public.bx_sales_order_id_seq') IS NOT NULL
       AND to_regclass('public.sales_order_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE public.bx_sales_order_id_seq RENAME TO sales_order_id_seq';
    END IF;
    IF to_regclass('public.bx_sales_order_line_id_seq') IS NOT NULL
       AND to_regclass('public.sales_order_line_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE public.bx_sales_order_line_id_seq RENAME TO sales_order_line_id_seq';
    END IF;
    IF to_regclass('public.bx_sales_order_line_tax_id_seq') IS NOT NULL
       AND to_regclass('public.sales_order_line_tax_id_seq') IS NULL THEN
        EXECUTE 'ALTER SEQUENCE public.bx_sales_order_line_tax_id_seq RENAME TO sales_order_line_tax_id_seq';
    END IF;

    -- If both legacy and standard tables exist, keep standard tables and remove legacy.
    IF to_regclass('public.bx_sales_order_line_tax') IS NOT NULL
       AND to_regclass('public.sales_order_line_tax') IS NOT NULL THEN
        EXECUTE 'DROP TABLE public.bx_sales_order_line_tax';
    END IF;

    IF to_regclass('public.bx_sales_order_line') IS NOT NULL
       AND to_regclass('public.sales_order_line') IS NOT NULL THEN
        EXECUTE 'DROP TABLE public.bx_sales_order_line';
    END IF;

    IF to_regclass('public.bx_sales_order') IS NOT NULL
       AND to_regclass('public.sales_order') IS NOT NULL THEN
        EXECUTE 'DROP TABLE public.bx_sales_order';
    END IF;

    IF to_regclass('public.bx_customer') IS NOT NULL
       AND to_regclass('public.customer') IS NOT NULL THEN
        EXECUTE 'DROP TABLE public.bx_customer';
    END IF;

    -- Drop legacy sequences if they remain after table cleanup.
    IF to_regclass('public.bx_sales_order_line_tax_id_seq') IS NOT NULL THEN
        EXECUTE 'DROP SEQUENCE public.bx_sales_order_line_tax_id_seq';
    END IF;
    IF to_regclass('public.bx_sales_order_line_id_seq') IS NOT NULL THEN
        EXECUTE 'DROP SEQUENCE public.bx_sales_order_line_id_seq';
    END IF;
    IF to_regclass('public.bx_sales_order_id_seq') IS NOT NULL THEN
        EXECUTE 'DROP SEQUENCE public.bx_sales_order_id_seq';
    END IF;
    IF to_regclass('public.bx_customer_id_seq') IS NOT NULL THEN
        EXECUTE 'DROP SEQUENCE public.bx_customer_id_seq';
    END IF;
END $$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0003_sales_order_state_paid"),
    ]

    operations = [
        migrations.RunSQL(sql=RENAME_SQL, reverse_sql=migrations.RunSQL.noop),
    ]

