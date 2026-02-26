from django.db.models.aggregates import Sum

from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


def get_certificate_balance(cpo=None):
    provision_certificates = ElecProvisionCertificate.objects.all()
    transfer_certificates = ElecTransferCertificate.objects.all()

    if cpo is not None:
        provision_certificates = provision_certificates.filter(cpo=cpo)
        transfer_certificates = transfer_certificates.filter(supplier=cpo)

    total_provision = provision_certificates.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
    total_transfer = transfer_certificates.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0

    return round(total_provision - total_transfer, 2)
