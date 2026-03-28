# partner.parent_id (self FK), partner.tax_id (NPWP) + unique_partner_tax_id — idempotent on PostgreSQL.

import django.db.models.deletion
from django.db import migrations, models


ADD_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'partner' AND column_name = 'parent_id'
  ) THEN
    ALTER TABLE public.partner ADD COLUMN parent_id integer;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_partner_parent'
  ) THEN
    ALTER TABLE public.partner
      ADD CONSTRAINT fk_partner_parent
      FOREIGN KEY (parent_id) REFERENCES public.partner (id) ON DELETE SET NULL;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'partner' AND column_name = 'tax_id'
  ) THEN
    ALTER TABLE public.partner ADD COLUMN tax_id character varying(50);
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'unique_partner_tax_id'
  ) THEN
    ALTER TABLE public.partner ADD CONSTRAINT unique_partner_tax_id UNIQUE (tax_id);
  END IF;
END $$;
"""

DROP_SQL = """
ALTER TABLE public.partner DROP CONSTRAINT IF EXISTS unique_partner_tax_id;
ALTER TABLE public.partner DROP COLUMN IF EXISTS tax_id;
ALTER TABLE public.partner DROP CONSTRAINT IF EXISTS fk_partner_parent;
ALTER TABLE public.partner DROP COLUMN IF EXISTS parent_id;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0014_merge_20260328_0447"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(ADD_SQL, DROP_SQL)],
            state_operations=[
                migrations.AddField(
                    model_name="partner",
                    name="parent",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child_partners",
                        to="sales.partner",
                        db_column="parent_id",
                    ),
                ),
                migrations.AddField(
                    model_name="partner",
                    name="tax_id",
                    field=models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="Tax ID (NPWP)",
                    ),
                ),
            ],
        ),
    ]
