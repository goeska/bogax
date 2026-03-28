# Case-insensitive Tax ID uniqueness via tax_id_norm (lower(strip(tax_id))).

from collections import defaultdict

from django.db import migrations, models


def _backfill_and_dedupe_tax_id_norm(apps, schema_editor):
    Partner = apps.get_model("sales", "Partner")
    for p in Partner.objects.all().iterator():
        if not p.tax_id or not str(p.tax_id).strip():
            Partner.objects.filter(pk=p.pk).update(tax_id=None, tax_id_norm=None)
        else:
            raw = str(p.tax_id).strip()
            Partner.objects.filter(pk=p.pk).update(tax_id=raw, tax_id_norm=raw.lower())

    groups = defaultdict(list)
    for p in Partner.objects.exclude(tax_id_norm__isnull=True).order_by("id"):
        groups[p.tax_id_norm].append(p.pk)

    for _norm, pks in groups.items():
        if len(pks) <= 1:
            continue
        for pk in pks[1:]:
            p = Partner.objects.get(pk=pk)
            suffix = f" (#{pk})"
            max_base = max(1, 50 - len(suffix))
            base = (str(p.tax_id).strip() or f"id{pk}")[:max_base].rstrip()
            new_tid = (f"{base}{suffix}")[:50]
            new_norm = new_tid.lower()
            Partner.objects.filter(pk=pk).update(tax_id=new_tid, tax_id_norm=new_norm)


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0010_table_number_unique_name_global"),
        ("sales", "0018_partner_unique_name_norm_corporate"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="tax_id_norm",
            field=models.CharField(
                blank=True, editable=False, max_length=50, null=True
            ),
        ),
        migrations.RunPython(_backfill_and_dedupe_tax_id_norm, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="partner",
            name="tax_id",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Tax ID (NPWP)"
            ),
        ),
        migrations.AddConstraint(
            model_name="partner",
            constraint=models.UniqueConstraint(
                condition=models.Q(("tax_id_norm__isnull", False)),
                fields=("tax_id_norm",),
                name="unique_partner_tax_id_norm",
                violation_error_message=(
                    "This Tax ID (NPWP) is already registered to another partner."
                ),
            ),
        ),
    ]
