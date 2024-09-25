from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.models import CarbureLotComment, Entity


class AddCommentSerializer(serializers.Serializer):
    comment = serializers.CharField()
    is_visible_by_admin = serializers.BooleanField(default=False)
    is_visible_by_auditor = serializers.BooleanField(default=False)


class AddCommentMixin:
    @action(methods=["post"], detail=False, url_path="add-comment")
    def add_comment(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)
        serializer = AddCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.validated_data["comment"]
        is_visible_by_admin = serializer.validated_data["is_visible_by_admin"]
        is_visible_by_auditor = serializer.validated_data["is_visible_by_auditor"]
        lots = self.filter_queryset(self.get_queryset())

        for lot in lots:
            if (
                lot.carbure_supplier != entity
                and lot.carbure_client != entity
                and entity.entity_type not in [Entity.AUDITOR, Entity.ADMIN]
            ):
                raise PermissionDenied({"message": "Entity not authorized to comment on this lot"})

            lot_comment = CarbureLotComment()
            lot_comment.entity = entity
            lot_comment.user = request.user
            lot_comment.lot = lot

            if entity.entity_type == Entity.AUDITOR:
                lot_comment.comment_type = CarbureLotComment.AUDITOR
                if is_visible_by_admin:
                    lot_comment.is_visible_by_admin = True
            elif entity.entity_type == Entity.ADMIN:
                lot_comment.comment_type = CarbureLotComment.ADMIN
                if is_visible_by_auditor:
                    lot_comment.is_visible_by_auditor = True
            else:
                lot_comment.comment_type = CarbureLotComment.REGULAR
            lot_comment.comment = comment
            lot_comment.save()

        return Response({"status": "success"})
