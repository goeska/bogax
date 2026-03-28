# Case-insensitive partner name uniqueness per is_corporate via name_norm (lower(trim(name))).

from collections import defaultdict

from django.db import migrations, models


def _sync_and_dedupe_partner_names(apps, schema_editor):
    Partner = apps.get_model("sales", "Partner")
    for p in Partner.objects.iterator():
        nn = (p.name or "").strip().lower()
        if p.name_norm != nn:
            Partner.objects.filter(pk=p.pk).update(name_norm=nn)

    groups = defaultdict(list)
    for p in Partner.objects.all().order_by("id"):
        key = ((p.name_norm or "").strip().lower(), p.is_corporate)
        groups[key].append(p.pk)

    for _key, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            p = Partner.objects.get(pk=pk)
            suffix = f" (#{pk})"
            max_base = max(1, 100 - len(suffix))
            base = ((p.name or "").strip() or f"id{pk}")[:max_base].rstrip()
            new_name = (f"{base}{suffix}")[:100]
            new_norm = new_name.strip().lower()
            Partner.objects.filter(pk=pk).update(name=new_name, name_norm=new_norm)


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0010_table_number_unique_name_global"),
        ("sales", "0017_partner_unique_name_corporate_message"),
    ]

    operations = [
        migrations.RunPython(_sync_and_dedupe_partner_names, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name="partner",
            name="unique_name_corporate",
        ),
        migrations.AddConstraint(
            model_name="partner",
            constraint=models.UniqueConstraint(
                fields=("name_norm", "is_corporate"),
                name="unique_name_norm_corporate",
                violation_error_message=(
                    "That name’s already taken for this partner type "
                    "(corporate vs non-corporate) — try another one."
                ),
            ),
        ),
    ]
