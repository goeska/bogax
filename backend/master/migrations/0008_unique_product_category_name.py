from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("master", "0007_unique_uom_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'product_category'
                  AND indexname = 'ux_product_category_name'
              ) THEN
                CREATE UNIQUE INDEX ux_product_category_name
                  ON public.product_category (name);
              END IF;
            END $$;
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS public.ux_product_category_name;
            """,
        )
    ]

