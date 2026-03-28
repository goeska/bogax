# Case-insensitive unique category name via name_norm (lower(trim(name))).

from collections import defaultdict

from django.db import migrations, models


ADD_NAME_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'product_category'
      AND column_name = 'name_norm'
  ) THEN
    ALTER TABLE public.product_category ADD COLUMN name_norm varchar(100);
  END IF;
END $$;

UPDATE public.product_category
SET name_norm = lower(trim(coalesce(name, '')))
WHERE name_norm IS NULL OR name_norm IS DISTINCT FROM lower(trim(coalesce(name, '')));

ALTER TABLE public.product_category
  ALTER COLUMN name_norm SET DEFAULT '',
  ALTER COLUMN name_norm SET NOT NULL;
"""

SWAP_UNIQUE_INDEX_SQL = """
DROP INDEX IF EXISTS public.ux_product_category_name;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'product_category'
      AND indexname = 'ux_product_category_name_norm'
  ) THEN
    CREATE UNIQUE INDEX ux_product_category_name_norm
      ON public.product_category (name_norm);
  END IF;
END $$;
"""

REVERSE_INDEX_SQL = """
DROP INDEX IF EXISTS public.ux_product_category_name_norm;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'product_category'
      AND indexname = 'ux_product_category_name'
  ) THEN
    CREATE UNIQUE INDEX ux_product_category_name
      ON public.product_category (name);
  END IF;
END $$;
"""


def _backfill_and_dedupe(apps, schema_editor):
    ProductCategory = apps.get_model("master", "ProductCategory")
    for p in ProductCategory.objects.all().iterator():
        raw = (p.name or "").strip()
        nn = raw.lower() if raw else ""
        ProductCategory.objects.filter(pk=p.pk).update(name=raw, name_norm=nn)

    groups = defaultdict(list)
    for p in ProductCategory.objects.all().order_by("id"):
        groups[p.name_norm].append(p.pk)

    for _norm, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            p = ProductCategory.objects.get(pk=pk)
            suffix = f" (#{pk})"
            max_base = max(1, 100 - len(suffix))
            base = ((p.name or "").strip() or f"id{pk}")[:max_base].rstrip()
            new_name = (f"{base}{suffix}")[:100]
            new_norm = new_name.strip().lower()
            ProductCategory.objects.filter(pk=pk).update(name=new_name, name_norm=new_norm)


class Migration(migrations.Migration):

    atomic = True

    dependencies = [
        ("master", "0010_table_number_unique_name_global"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(ADD_NAME_NORM_SQL, migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="productcategory",
                    name="name_norm",
                    field=models.CharField(
                        blank=True, default="", editable=False, max_length=100
                    ),
                ),
            ],
        ),
        migrations.RunPython(_backfill_and_dedupe, migrations.RunPython.noop),
        migrations.RunSQL(SWAP_UNIQUE_INDEX_SQL, REVERSE_INDEX_SQL),
    ]
