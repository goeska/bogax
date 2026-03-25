from rest_framework import serializers

from .models import PaymentWithSource


class PaymentReadSerializer(serializers.ModelSerializer):
    type_label = serializers.SerializerMethodField()
    source_summary = serializers.SerializerMethodField()

    def get_type_label(self, obj):
        return "Incoming" if obj.tx_type == "i" else "Outgoing"

    def get_source_summary(self, obj):
        return {
            "table": obj.source_table,
            "id": obj.source_id if obj.source_id is not None else obj.source_pk,
            "code": obj.source_code or obj.reference_code,
            "state": obj.source_state or "",
            "transaction_at": obj.source_transaction_at or obj.transaction_at,
            "party_name": obj.source_party_name or "",
            "party_phone": obj.source_party_phone or "",
        }

    class Meta:
        model = PaymentWithSource
        fields = (
            "id",
            "tx_type",
            "type_label",
            "source_table",
            "source_pk",
            "reference_code",
            "amount",
            "currency_code",
            "transaction_at",
            "note",
            "created_by_id",
            "created_by_email",
            "source_summary",
            "created_at",
            "updated_at",
        )
