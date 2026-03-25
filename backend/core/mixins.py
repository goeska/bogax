"""
Shared API behaviour for models with an ``is_active`` flag (master data,
``accounts.User``, future sales entities, etc.).

Use :class:`SoftDeactivateDestroyMixin` on any ``ModelViewSet`` where
removing a row should mean ``UPDATE ... SET is_active = FALSE`` rather than
``DELETE``. List/retrieve/update/destroy only see rows with ``is_active=True``.
"""


class SoftDeactivateDestroyMixin:
    """Expose only active rows; HTTP DELETE sets ``is_active=False`` (no SQL DELETE)."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
