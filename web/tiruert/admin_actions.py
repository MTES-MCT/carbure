from django.db import transaction

from tiruert.models.operation import Operation


def perform_bulk_operations_validation(modeladmin, request, queryset):
    """
    Validates all selected 'INCORPORATION', 'CESSION', 'EXPORTATION' or 'EXPEDITION' operations in bulk.
    """
    status_by_type = {
        Operation.INCORPORATION: Operation.VALIDATED,
        Operation.EXPORTATION: Operation.VALIDATED,
        Operation.EXPEDITION: Operation.VALIDATED,
        Operation.CESSION: Operation.ACCEPTED,
    }

    with transaction.atomic():
        for obj in queryset:
            if obj.status == Operation.PENDING:
                new_status = status_by_type.get(obj.type)
                if new_status:
                    obj.status = new_status
                    obj.save()

    modeladmin.message_user(request, "Les opérations ont été validées avec succès.")


perform_bulk_operations_validation.short_description = "Valider les opérations sélectionnées"
