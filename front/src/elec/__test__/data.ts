import { EntityPreview, EntityType } from "carbure/types";
import { ElecProvisionCertificatePreview } from "elec/types";
import { ElecProvisionCertificatesData } from "elec/types-cpo";



export const elecProvisionCertificateCPOPreview: EntityPreview = {
    id: 10,
    name: "Producteur Test MTES",
    entity_type: EntityType.Producer
}
export const elecProvisionCertificatePreview: ElecProvisionCertificatePreview =
{
    id: 1,
    cpo: elecProvisionCertificateCPOPreview,
    quarter: 1,
    year: 2023,
    operating_unit: "FRIONE",
    energy_amount: 200000,
    remaining_energy_amount: 200000
}
export const elecAdminProvisionCertificateList: ElecProvisionCertificatesData = {
    elec_provision_certificates: [elecProvisionCertificatePreview],
    from: 0,
    ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
    returned: 10,
    total: 11
}