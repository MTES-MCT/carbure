from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.elec_audit_repository import ElecAuditRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_years(request):
    audits = ElecAuditRepository.get_audited_applications(request.user)
    years = audits.values_list("created_at__year", flat=True)
    return SuccessResponse(list(set(years)))
