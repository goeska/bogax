# Case-insensitive product name per category: (name_norm, product_category_id) unique.

from collections import defaultdict

from django.db import connection, migrations, models


ADD_NAME_NORM_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'product'
      AND column_name = 'name_norm'
  ) THEN
    ALTER TABLE public.product ADD COLUMN name_norm varchar(255);
  END IF;
END $$;

UPDATE public.product
SET name_norm = lower(trim(coalesce(name, '')))
WHERE name_norm IS NULL OR name_norm IS DISTINCT FROM lower(trim(coalesce(name, '')));

ALTER TABLE public.product
  ALTER COLUMN name_norm SET DEFAULT '',
  ALTER COLUMN name_norm SET NOT NULL;
"""

ADD_UNIQUE_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'product'
      AND indexname = 'ux_product_name_norm_category'
  ) THEN
    CREATE UNIQUE INDEX ux_product_name_norm_category
      ON public.product (name_norm, product_category_id);
  END IF;
END $$;
"""

DROP_UNIQUE_SQL = """
DROP INDEX IF EXISTS public.ux_product_name_norm_category;
"""


def _backfill_and_dedupe(apps, schema_editor):
    Product = apps.get_model("master", "Product")
    for p in Product.objects.all().iterator():
        raw = (p.name or "").strip()
        nn = raw.lower() if raw else ""
        Product.objects.filter(pk=p.pk).update(name=raw, name_norm=nn)

    # Historical migration state may omit FK attnames; use SQL for category id.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, name_norm, product_category_id FROM public.product ORDER BY id"
        )
        id_norm_cat = cursor.fetchall()

    groups = defaultdict(list)
    for pid, nn, cid in id_norm_cat:
        groups[(nn, cid)].append(pid)

    for _key, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM public.product WHERE id = %s", [pk])
                row = cursor.fetchone()
                cur_name = (row[0] or "").strip() if row else ""
            suffix = f" (#{pk})"
            max_base = max(1, 255 - len(suffix))
            base = (cur_name or f"id{pk}")[:max_base].rstrip()
            new_name = (f"{base}{suffix}")[:255]
            new_norm = new_name.strip().lower()
            Product.objects.filter(pk=pk).update(name=new_name, name_norm=new_norm)


class Migration(migrations.Migration):

    atomic = True

    dependencies = [
        ("master", "0011_product_category_name_norm"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(ADD_NAME_NORM_SQL, migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="product",
                    name="name_norm",
                    field=models.CharField(
                        blank=True, default="", editable=False, max_length=255
                    ),
                ),
            ],
        ),
        migrations.RunPython(_backfill_and_dedupe, migrations.RunPython.noop),
        migrations.RunSQL(ADD_UNIQUE_SQL, DROP_UNIQUE_SQL),
    ]
