# Case-insensitive UOM name: name_norm + unique index (replaces ux_uom_name on raw name).

from collections import defaultdict

from django.db import migrations, models


DROP_OLD_UNIQUE_SQL = """
DROP INDEX IF EXISTS public.ux_uom_name;
"""

ADD_NAME_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'uom'
      AND column_name = 'name_norm'
  ) THEN
    ALTER TABLE public.uom ADD COLUMN name_norm varchar(100);
  END IF;
END $$;

UPDATE public.uom
SET name_norm = lower(trim(coalesce(name, '')))
WHERE name_norm IS NULL OR name_norm IS DISTINCT FROM lower(trim(coalesce(name, '')));

ALTER TABLE public.uom
  ALTER COLUMN name_norm SET DEFAULT '',
  ALTER COLUMN name_norm SET NOT NULL;
"""

ADD_UNIQUE_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'uom'
      AND indexname = 'ux_uom_name_norm'
  ) THEN
    CREATE UNIQUE INDEX ux_uom_name_norm ON public.uom (name_norm);
  END IF;
END $$;
"""

DROP_UNIQUE_NORM_SQL = """
DROP INDEX IF EXISTS public.ux_uom_name_norm;
"""

RECREATE_OLD_UNIQUE_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'uom'
      AND indexname = 'ux_uom_name'
  ) THEN
    CREATE UNIQUE INDEX ux_uom_name ON public.uom (name);
  END IF;
END $$;
"""


def _backfill_and_dedupe(apps, schema_editor):
    Uom = apps.get_model("master", "Uom")
    for p in Uom.objects.all().iterator():
        raw = (p.name or "").strip()
        nn = raw.lower() if raw else ""
        Uom.objects.filter(pk=p.pk).update(name=raw, name_norm=nn)

    groups = defaultdict(list)
    for p in Uom.objects.all().order_by("id"):
        groups[p.name_norm].append(p.pk)

    for _norm, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            u = Uom.objects.get(pk=pk)
            suffix = f" (#{pk})"
            max_base = max(1, 100 - len(suffix))
            base = ((u.name or "").strip() or f"id{pk}")[:max_base].rstrip()
            new_name = (f"{base}{suffix}")[:100]
            new_norm = new_name.strip().lower()
            Uom.objects.filter(pk=pk).update(name=new_name, name_norm=new_norm)


class Migration(migrations.Migration):

    atomic = True

    dependencies = [
        ("master", "0013_product_name_norm_global"),
    ]

    operations = [
        migrations.RunSQL(DROP_OLD_UNIQUE_SQL, RECREATE_OLD_UNIQUE_SQL),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(ADD_NAME_NORM_SQL, migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="uom",
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
