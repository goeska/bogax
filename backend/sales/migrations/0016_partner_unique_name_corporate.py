# UNIQUE (name, is_corporate) on partner — idempotent on PostgreSQL.

from django.db import migrations, models


ADD_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'unique_name_corporate'
  ) THEN
    ALTER TABLE public.partner
      ADD CONSTRAINT unique_name_corporate UNIQUE (name, is_corporate);
  END IF;
END $$;
"""

DROP_SQL = """
ALTER TABLE public.partner DROP CONSTRAINT IF EXISTS unique_name_corporate;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0015_partner_parent_tax_id"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(ADD_SQL, DROP_SQL)],
            state_operations=[
                migrations.AddConstraint(
                    model_name="partner",
                    constraint=models.UniqueConstraint(
                        fields=("name", "is_corporate"),
                        name="unique_name_corporate",
                    ),
                ),
            ],
        ),
    ]
