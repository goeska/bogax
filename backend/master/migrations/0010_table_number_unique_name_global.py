# Aligns DB with Resto Table master: UNIQUE(name) on all rows (not only active).

from django.db import migrations


ADD_UNIQUE_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint c
    JOIN pg_class t ON c.conrelid = t.oid
    JOIN pg_namespace n ON t.relnamespace = n.oid
    WHERE n.nspname = 'public'
      AND t.relname = 'table_number'
      AND c.conname = 'unique_table_number_name'
      AND c.contype = 'u'
  ) THEN
    ALTER TABLE public.table_number
      ADD CONSTRAINT unique_table_number_name UNIQUE (name);
  END IF;
END $$;
"""

DROP_UNIQUE_SQL = """
ALTER TABLE public.table_number DROP CONSTRAINT IF EXISTS unique_table_number_name;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("master", "0009_legal_entity_type_state_only"),
    ]

    operations = [
        migrations.RunSQL(sql=ADD_UNIQUE_SQL, reverse_sql=DROP_UNIQUE_SQL),
    ]
