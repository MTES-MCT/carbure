from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.utils import CarbureEnv
from elec.models import ElecChargePointApplication
from elec.models.elec_audit_sample import ElecAuditSample


def send_email_to_cpo(application: ElecChargePointApplication):
    charge_point_count = application.elec_charge_points.count()
    charge_point_link = f"{CarbureEnv.get_base_url()}/org/{application.cpo.pk}/settings#elec-charge-points"

    text_message = f"""
    Bonjour,

    La DGEC vient de valider l'inscription de {charge_point_count} points de recharge.
    Vous pouvez les retrouver dans votre espace CarbuRe via <a href="{charge_point_link}">ce lien</a>.

    Merci beaucoup

    Bien cordialement,
    L'équipe CarbuRe
    """

    send_mail(
        subject=f"[CarbuRe] Inscription de {charge_point_count} points de recharge validée",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["carbure@beta.gouv.fr"],
        fail_silently=False,
    )


class AcceptApplicationSerializer(serializers.Serializer):
    force_validation = serializers.BooleanField(required=False)


class AcceptActionMixin:
    @action(methods=["post"], detail=True)
    def accept(self, request, id=None):
        application = get_object_or_404(ElecChargePointApplication, id=id)

        serializer = AcceptApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        force_validation = serializer.validated_data["force_validation"]

        if application.status in (
            ElecChargePointApplication.ACCEPTED,
            ElecChargePointApplication.REJECTED,
        ):
            raise ValidationError({"message": "Application has already been checked by admin"})

        if application.status == ElecChargePointApplication.PENDING and not force_validation:
            raise ValidationError({"message": "Application cannot be accepted if audit is not started"})

        application.status = ElecChargePointApplication.ACCEPTED
        application.save(update_fields=["status"])

        # marque l'échantillon comme "audité"
        audit_sample = application.audit_sample.first()
        if audit_sample:
            audit_sample.status = ElecAuditSample.AUDITED
            audit_sample.save()

        send_email_to_cpo(application)

        return Response({}, status=status.HTTP_200_OK)
