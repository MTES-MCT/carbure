class ListMixin:
    def list(self, request, *args, **kwargs):
        # entity_id = self.request.query_params.get("entity_id")
        # entity = Entity.objects.get(id=entity_id)
        lots = self.filter_queryset(self.get_queryset())

        # data["total_errors"] = total_errors
        # data["total_deadline"] = total_deadline
        # data["errors"] = get_lots_errors(lots, entity)
        # Pagination
        page = self.paginate_queryset(lots)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            # page_size = self.paginator.page_size
            # current_page = self.paginator.page.number
            # start_index = (current_page - 1) * page_size
            # lots =lots[:10]
            # total_errors, total_deadline = count_lots_of_interest(lots, entity)
            # additional_data = {
            #     "total_errors": total_errors,
            #     "total_deadline": total_deadline,
            #     'errors': get_lots_errors(lots, entity),
            # }
            paginated_response = self.get_paginated_response(data)
            # paginated_response.data.update(additional_data)
            return paginated_response
