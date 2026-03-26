from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("master", "0006_fix_table_number_unique_name_to_active_only"),
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
                  AND tablename = 'uom'
                  AND indexname = 'ux_uom_name'
              ) THEN
                CREATE UNIQUE INDEX ux_uom_name ON public.uom (name);
              END IF;
            END $$;
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS public.ux_uom_name;
            """,
        )
    ]

