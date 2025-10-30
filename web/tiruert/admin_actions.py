from django.db import transaction

from tiruert.models.operation import Operation


def perform_bulk_operations_validation(modeladmin, request, queryset):
    """
    Validates all selected 'INCORPORATION', 'CESSION', 'EXPORTATION' or 'EXPEDITION' operations in bulk.
    """
    with transaction.atomic():
        for obj in queryset:
            if obj.status == Operation.PENDING:
                if obj.type in [Operation.INCORPORATION, Operation.EXPORTATION, Operation.EXPEDITION]:
                    obj.status = Operation.VALIDATED
                elif obj.type == Operation.CESSION:
                    obj.status = Operation.ACCEPTED
                else:
                    continue  # Skip all other operation types
                obj.save()

    modeladmin.message_user(request, "Les opérations ont été validées avec succès.")


perform_bulk_operations_validation.short_description = "Valider les opérations sélectionnées"
