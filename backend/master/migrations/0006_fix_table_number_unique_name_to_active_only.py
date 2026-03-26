from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("master", "0005_unique_active_table_number_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- If there is an existing UNIQUE constraint/index that enforces
            -- table_number(name) uniqueness for ALL rows, drop it.
            --
            -- We keep the partial unique index:
            --   ux_table_number_name_active ON table_number(name) WHERE is_active = true

            DO $$
            DECLARE
              c RECORD;
              idx RECORD;
            BEGIN
              -- Drop UNIQUE constraints that involve only column "name" on table_number.
              FOR c IN
                SELECT conname
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                WHERE con.contype = 'u'
                  AND nsp.nspname = 'public'
                  AND rel.relname = 'table_number'
                  AND (
                    SELECT array_agg(att.attname ORDER BY att.attnum)
                    FROM unnest(con.conkey) AS k(attnum)
                    JOIN pg_attribute att
                      ON att.attrelid = rel.oid AND att.attnum = k.attnum
                  )::text[] = ARRAY['name']::text[]
              LOOP
                EXECUTE format('ALTER TABLE public.table_number DROP CONSTRAINT %I', c.conname);
              END LOOP;

              -- Drop UNIQUE indexes on (name) without a WHERE clause (not partial),
              -- excluding our intended partial unique index.
              FOR idx IN
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'table_number'
                  AND indexdef ILIKE 'create unique index%'
                  AND indexname <> 'ux_table_number_name_active'
                  AND indexdef ILIKE '%(name)%'
                  AND indexdef NOT ILIKE '% where %'
              LOOP
                EXECUTE format('DROP INDEX IF EXISTS public.%I', idx.indexname);
              END LOOP;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        )
    ]

