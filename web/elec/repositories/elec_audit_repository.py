from django.db.models import Count

from core.models import Entity, UserRights
from elec.models.elec_audit_sample import ElecAuditSample


class ElecAuditRepository:
    @staticmethod
    def get_audited_cpos(audit_user):
        cpo_audit_rights = UserRights.objects.select_related("entity").filter(
            user=audit_user,
            role=UserRights.AUDITOR,
            entity__entity_type=Entity.CPO,
        )

        return Entity.objects.filter(id__in=[cpo.entity.id for cpo in cpo_audit_rights])

    @staticmethod
    def get_audited_applications(audit_user, **filters):
        cpos = ElecAuditRepository.get_audited_cpos(audit_user)

        audits = (
            ElecAuditSample.objects.select_related("cpo", "charge_point_application", "meter_reading_application")
            .filter(cpo__in=cpos)
            .order_by("created_at")
            .annotate(
                station_count=Count("audited_charge_points__charge_point__station_id", distinct=True),
                charge_point_count=Count("audited_charge_points__id"),
            )
        )

        if filters.get("year"):
            audits = audits.filter(created_at__year=filters["year"])

        if filters.get("cpo"):
            audits = audits.filter(cpo__name__in=filters["cpo"])

        if filters.get("status") == "IN_PROGRESS":
            audits = audits.filter(status=ElecAuditSample.IN_PROGRESS)
        elif filters.get("status") == "AUDITED":
            audits = audits.filter(status=ElecAuditSample.AUDITED)

        return audits

    @staticmethod
    def get_audited_sample_by_id(audit_user, audit_sample_id):
        applications = ElecAuditRepository.get_audited_applications(audit_user)
        return applications.filter(id=audit_sample_id).first()
