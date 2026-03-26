from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("master", "0004_rename_legacy_created_at_to_update_at"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- 1) Make migration robust: if there are duplicate ACTIVE table numbers,
            --    keep the smallest id active and deactivate the rest.
            WITH dups AS (
              SELECT
                name,
                array_agg(id ORDER BY id) AS ids
              FROM table_number
              WHERE is_active = TRUE
              GROUP BY name
              HAVING COUNT(*) > 1
            )
            UPDATE table_number
            SET is_active = FALSE
            WHERE id IN (
              SELECT unnest(ids[2:]) FROM dups
            );

            -- 2) Enforce uniqueness for ACTIVE rows only.
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'table_number'
                  AND indexname = 'ux_table_number_name_active'
              ) THEN
                CREATE UNIQUE INDEX ux_table_number_name_active
                  ON public.table_number (name)
                  WHERE is_active = TRUE;
              END IF;
            END $$;
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS public.ux_table_number_name_active;
            """,
        ),
    ]

