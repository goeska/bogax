from django.db import migrations, models


def _normalize_name(value):
    return (value or "").strip().lower()


def _normalize_phone(value):
    return (value or "").strip()


def cleanup_and_fill_partner_norm(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Partner = apps.get_model("sales", "Partner")
    SalesOrder = apps.get_model("sales", "SalesOrder")
    PurchaseOrder = apps.get_model("purchase", "PurchaseOrder")

    partners = list(
        Partner.objects.using(db_alias).all().order_by("id").values(
            "id",
            "name",
            "phone",
            "is_customer",
            "is_vendor",
            "is_active",
            "name_norm",
            "phone_norm",
        )
    )

    groups = {}
    for p in partners:
        key = (_normalize_name(p["name"]), _normalize_phone(p["phone"]))
        groups.setdefault(key, []).append(p)

    for (name_norm, phone_norm), rows in groups.items():
        rows = sorted(rows, key=lambda r: r["id"])
        keeper = rows[0]
        keeper_id = keeper["id"]
        other_ids = [r["id"] for r in rows[1:]]

        is_customer_any = any(r["is_customer"] for r in rows)
        is_vendor_any = any(r["is_vendor"] for r in rows)
        is_active_any = any(r["is_active"] for r in rows)

        Partner.objects.using(db_alias).filter(pk=keeper_id).update(
            name=(keeper["name"] or "").strip(),
            phone=(keeper["phone"] or "").strip(),
            name_norm=name_norm,
            phone_norm=phone_norm,
            is_customer=is_customer_any,
            is_vendor=is_vendor_any,
            is_active=is_active_any,
        )

        if other_ids:
            SalesOrder.objects.using(db_alias).filter(partner_id__in=other_ids).update(
                partner_id=keeper_id
            )
            PurchaseOrder.objects.using(db_alias).filter(partner_id__in=other_ids).update(
                partner_id=keeper_id
            )
            Partner.objects.using(db_alias).filter(pk__in=other_ids).delete()

    # Ensure all remaining rows have normalized values populated.
    for p in Partner.objects.using(db_alias).all().only("id", "name", "phone"):
        Partner.objects.using(db_alias).filter(pk=p.pk).update(
            name_norm=_normalize_name(p.name),
            phone_norm=_normalize_phone(p.phone),
        )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("sales", "0007_partner_is_active"),
        ("purchase", "0002_purchase_order_partner_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="name_norm",
            field=models.CharField(db_index=True, default="", editable=False, max_length=100),
        ),
        migrations.AddField(
            model_name="partner",
            name="phone_norm",
            field=models.CharField(db_index=True, default="", editable=False, max_length=50),
        ),
        migrations.RunPython(cleanup_and_fill_partner_norm, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name="partner",
            name="unique_name_phone",
        ),
        migrations.AddConstraint(
            model_name="partner",
            constraint=models.UniqueConstraint(
                fields=("name_norm", "phone_norm"),
                name="unique_partner_name_norm_phone_norm",
            ),
        ),
    ]

