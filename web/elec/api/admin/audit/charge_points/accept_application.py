from django import forms
from django.conf import settings
from django.http import HttpRequest
from django.core.mail import send_mail

from django.views.decorators.http import require_POST
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import CarbureEnv
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point_application import ElecChargePointApplication


class AcceptApplicationForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecChargePointApplication.objects.all())
    force_validation = forms.BooleanField(required=False)


class AcceptApplicationError:
    AUDIT_NOT_STARTED = "AUDIT_NOT_STARTED"
    ALREADY_CHECKED = "ALREADY_CHECKED"


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def accept_application(request: HttpRequest):
    form = AcceptApplicationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    force_validation = form.cleaned_data["force_validation"]

    if application.status in (ElecChargePointApplication.ACCEPTED, ElecChargePointApplication.REJECTED):
        return ErrorResponse(400, AcceptApplicationError.ALREADY_CHECKED, "Application has already been checked by admin")

    if application.status == ElecChargePointApplication.PENDING and not force_validation:
        return ErrorResponse(
            400, AcceptApplicationError.AUDIT_NOT_STARTED, "Application cannot be accepted if audit is not started"
        )

    application.status = ElecChargePointApplication.ACCEPTED
    application.save()

    # marque l'échantillon comme "audité"
    audit_sample = application.audit_sample.first()
    if audit_sample:
        audit_sample.status = ElecAuditSample.AUDITED
        audit_sample.save()

    send_email_to_cpo(application)

    return SuccessResponse()


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
