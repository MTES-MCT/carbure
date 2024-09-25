from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from elec.models import ElecChargePointApplication


class RejectApplicationSerializer(serializers.Serializer):
    force_rejection = serializers.BooleanField(required=False)


class RejectActionMixin:
    @action(methods=["post"], detail=True)
    def reject(self, request, id=None):
        application = get_object_or_404(ElecChargePointApplication, id=id)

        serializer = RejectApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        force_rejection = serializer.validated_data["force_rejection"]

        if application.status in (
            ElecChargePointApplication.ACCEPTED,
            ElecChargePointApplication.REJECTED,
        ):
            raise ValidationError({"message": "Application has already been checked by admin"})

        if application.status == ElecChargePointApplication.PENDING and not force_rejection:
            raise ValidationError({"message": "Application cannot be rejected if audit is not started"})

        application.status = ElecChargePointApplication.REJECTED
        application.save(update_fields=["status"])

        return Response({}, status=status.HTTP_200_OK)
