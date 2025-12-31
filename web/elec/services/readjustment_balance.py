from django.db.models.aggregates import Sum

from elec.models.elec_certificate_readjustment import ElecCertificateReadjustment
from elec.models.elec_transfer_certificate import ElecTransferCertificate


def get_readjustment_balance(cpo):
    expected_readjustment_dict = ElecCertificateReadjustment.objects.filter(cpo=cpo).aggregate(Sum("energy_amount"))
    expected_readjustment = expected_readjustment_dict.get("energy_amount__sum") or 0
    confirmed_readjustment_dict = ElecTransferCertificate.objects.filter(supplier=cpo, is_readjustment=True).aggregate(
        Sum("energy_amount")
    )
    confirmed_readjustment = confirmed_readjustment_dict.get("energy_amount__sum") or 0
    return round(expected_readjustment - confirmed_readjustment, 2)
