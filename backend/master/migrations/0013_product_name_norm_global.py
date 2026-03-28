# Global case-insensitive product name: unique(name_norm).

from collections import defaultdict

from django.db import connection, migrations


DROP_CATEGORY_UNIQUE_SQL = """
DROP INDEX IF EXISTS public.ux_product_name_norm_category;
"""

ADD_GLOBAL_UNIQUE_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'product'
      AND indexname = 'ux_product_name_norm'
  ) THEN
    CREATE UNIQUE INDEX ux_product_name_norm
      ON public.product (name_norm);
  END IF;
END $$;
"""

DROP_GLOBAL_UNIQUE_SQL = """
DROP INDEX IF EXISTS public.ux_product_name_norm;
"""

RECREATE_CATEGORY_UNIQUE_SQL = """
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


def _dedupe_global_name_norm(apps, schema_editor):
    Product = apps.get_model("master", "Product")
    for p in Product.objects.all().iterator():
        raw = (p.name or "").strip()
        nn = raw.lower() if raw else ""
        Product.objects.filter(pk=p.pk).update(name=raw, name_norm=nn)

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name_norm FROM public.product ORDER BY id")
        rows = cursor.fetchall()

    groups = defaultdict(list)
    for pid, nn in rows:
        groups[nn].append(pid)

    for _nn, pks in groups.items():
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


def _dedupe_global_name_norm_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    atomic = True

    dependencies = [
        ("master", "0012_product_name_norm"),
    ]

    operations = [
        migrations.RunPython(_dedupe_global_name_norm, _dedupe_global_name_norm_reverse),
        migrations.RunSQL(DROP_CATEGORY_UNIQUE_SQL, RECREATE_CATEGORY_UNIQUE_SQL),
        migrations.RunSQL(ADD_GLOBAL_UNIQUE_SQL, DROP_GLOBAL_UNIQUE_SQL),
    ]
