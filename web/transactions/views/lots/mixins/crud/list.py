from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin

from core.helpers import count_lots_of_interest, get_lots_errors
from core.models import Entity


class ListMixin(ListModelMixin):
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        status = self.request.query_params.get("status")
        selection = self.request.query_params.get("selection")
        if not status and not selection:
            raise ValidationError({"message": "MISSING_STATUS"})
        entity = Entity.objects.get(id=entity_id)
        lots = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(lots)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            page_size = self.paginator.page_size
            current_page = self.paginator.page.number
            start_index = (current_page - 1) * page_size

            total_errors, total_deadline = count_lots_of_interest(lots, entity)
            lots = lots[start_index : start_index + page_size]

            additional_data = {
                "total_errors": total_errors,
                "total_deadline": total_deadline,
                "errors": get_lots_errors(lots, entity),
            }
            paginated_response = self.get_paginated_response(data)

            paginated_response.data.update(additional_data)
            return paginated_response
