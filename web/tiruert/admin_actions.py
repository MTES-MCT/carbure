from django.db import transaction

from tiruert.models.operation import Operation


def perform_bulk_operations_validation(modeladmin, request, queryset):
    """
    Validates all selected 'INCORPORATION' or 'CESSION' operations in bulk.
    """
    with transaction.atomic():
        for obj in queryset:
            if obj.status == Operation.PENDING:
                if obj.type == Operation.INCORPORATION:
                    obj.status = Operation.VALIDATED
                elif obj.type == Operation.CESSION:
                    obj.status = Operation.ACCEPTED
                obj.save()

    modeladmin.message_user(request, "Les opérations ont été validées avec succès.")


perform_bulk_operations_validation.short_description = "Valider les opérations sélectionnées"
