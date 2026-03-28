# Case-insensitive tax name: name_norm + unique index.

from collections import defaultdict

from django.db import migrations, models


ADD_NAME_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'tax'
      AND column_name = 'name_norm'
  ) THEN
    ALTER TABLE public.tax ADD COLUMN name_norm varchar(100);
  END IF;
END $$;

UPDATE public.tax
SET name_norm = lower(trim(coalesce(name, '')))
WHERE name_norm IS NULL OR name_norm IS DISTINCT FROM lower(trim(coalesce(name, '')));

ALTER TABLE public.tax
  ALTER COLUMN name_norm SET DEFAULT '',
  ALTER COLUMN name_norm SET NOT NULL;
"""

ADD_UNIQUE_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'tax'
      AND indexname = 'ux_tax_name_norm'
  ) THEN
    CREATE UNIQUE INDEX ux_tax_name_norm ON public.tax (name_norm);
  END IF;
END $$;
"""

DROP_UNIQUE_NORM_SQL = """
DROP INDEX IF EXISTS public.ux_tax_name_norm;
"""


def _backfill_and_dedupe(apps, schema_editor):
    Tax = apps.get_model("master", "Tax")
    for p in Tax.objects.all().iterator():
        raw = (p.name or "").strip()
        nn = raw.lower() if raw else ""
        Tax.objects.filter(pk=p.pk).update(name=raw, name_norm=nn)

    groups = defaultdict(list)
    for p in Tax.objects.all().order_by("id"):
        groups[p.name_norm].append(p.pk)

    for _norm, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            t = Tax.objects.get(pk=pk)
            suffix = f" (#{pk})"
            max_base = max(1, 100 - len(suffix))
            base = ((t.name or "").strip() or f"id{pk}")[:max_base].rstrip()
            new_name = (f"{base}{suffix}")[:100]
            new_norm = new_name.strip().lower()
            Tax.objects.filter(pk=pk).update(name=new_name, name_norm=new_norm)


class Migration(migrations.Migration):

    atomic = True

    dependencies = [
        ("master", "0014_uom_name_norm"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(ADD_NAME_NORM_SQL, migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="tax",
                    name="name_norm",
                    field=models.CharField(
                        blank=True, default="", editable=False, max_length=100
                    ),
                ),
            ],
        ),
        migrations.RunPython(_backfill_and_dedupe, migrations.RunPython.noop),
        migrations.RunSQL(ADD_UNIQUE_NORM_SQL, DROP_UNIQUE_NORM_SQL),
    ]
