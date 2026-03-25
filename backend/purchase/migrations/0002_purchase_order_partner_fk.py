import django.db.models.deletion
from django.db import migrations, models


def forwards_copy_vendor_to_partner(apps, schema_editor):
    PurchaseOrder = apps.get_model("purchase", "PurchaseOrder")
    Partner = apps.get_model("sales", "Partner")
    for po in PurchaseOrder.objects.all().iterator():
        name = (po.vendor_name or "").strip()
        phone = (po.vendor_phone or "").strip()
        if not name:
            # Keep migration safe if legacy row had empty vendor name.
            name = f"Unknown Vendor #{po.id}"
        partner, _ = Partner.objects.update_or_create(
            name=name,
            phone=phone,
            defaults={"is_vendor": True},
        )
        if not partner.is_vendor:
            partner.is_vendor = True
            partner.save(update_fields=["is_vendor"])
        po.partner_id = partner.id
        po.save(update_fields=["partner_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0005_partner_and_sales_order_fk"),
        ("purchase", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="partner",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="purchase_orders",
                to="sales.partner",
            ),
        ),
        migrations.RunPython(forwards_copy_vendor_to_partner, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="purchaseorder",
            name="partner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="purchase_orders",
                to="sales.partner",
            ),
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="vendor_name",
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="vendor_phone",
        ),
    ]

