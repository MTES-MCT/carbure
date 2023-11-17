import { EntityPreview, EntityType } from "carbure/types";
import { ChargingPointsSubscriptionError, ElecChargingPointsSubscription, ElecChargingPointsSubscriptionCheckInfo, ElecChargingPointsSubscriptionStatus, ElecProvisionCertificatePreview } from "elec/types";
import { ElecCPOSnapshot, ElecProvisionCertificatesData } from "elec/types-cpo";

export const elecSnapshot: ElecCPOSnapshot = {
    provisioned_energy: 650000,
    remaining_energy: 500000,
    provision_certificates_available: 2,
    provision_certificates_history: 0,
    transferred_energy: 150000,
    transfer_certificates_pending: 1,
    transfer_certificates_accepted: 0,
    transfer_certificates_rejected: 0,
}

export const elecProvisionCertificateCPOPreview: EntityPreview = {
    id: 10,
    name: "Producteur Test MTES",
    entity_type: EntityType.Producer
}
const elecProvisionCertificatePreview: ElecProvisionCertificatePreview =
{
    id: 1,
    cpo: elecProvisionCertificateCPOPreview,
    quarter: 2,
    year: 2023,
    operating_unit: "FRIONE",
    energy_amount: 200000,
    remaining_energy_amount: 200000
}

const elecProvisionCertificatePreview2: ElecProvisionCertificatePreview =
{
    id: 1,
    cpo: elecProvisionCertificateCPOPreview,
    quarter: 1,
    year: 2023,
    operating_unit: "ORIONE",
    energy_amount: 450000,
    remaining_energy_amount: 300000
}

export const elecAdminProvisionCertificateList: ElecProvisionCertificatesData = {
    elec_provision_certificates: [elecProvisionCertificatePreview, elecProvisionCertificatePreview2],
    from: 0,
    ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
    returned: 10,
    total: 11
}


const elecChargingPointSubscription1: ElecChargingPointsSubscription = {
    id: 1,
    station_count: 4,
    charging_point_count: 90,
    power_total: 8,
    date: "2023-10-12",
    status: ElecChargingPointsSubscriptionStatus.Pending,
}

const elecChargingPointSubscription2: ElecChargingPointsSubscription = {
    id: 1,
    station_count: 19,
    charging_point_count: 987,
    power_total: 30000,
    date: "2023-11-13",
    status: ElecChargingPointsSubscriptionStatus.Accepted,
}
const elecChargingPointSubscription3: ElecChargingPointsSubscription = {
    id: 1,
    station_count: 1,
    charging_point_count: 5,
    power_total: 1000,
    date: "2023-09-01",
    status: ElecChargingPointsSubscriptionStatus.Rejected,
}

export const elecChargingPointsSubscriptions: ElecChargingPointsSubscription[] = [
    elecChargingPointSubscription1,
    elecChargingPointSubscription2,
    elecChargingPointSubscription3
]


export const chargingPointsSubscriptionError1: ChargingPointsSubscriptionError = {
    error: "MISSING_CHARGING_POINT_IN_DATAGOUV",
    meta: {
        charging_points: ["8U7Y", "8U7Y"]
    }
}
export const chargingPointsSubscriptionError2: ChargingPointsSubscriptionError = {
    error: "UNKNOW_ERROR"
}
export const elecChargingPointsSubscriptionCheckResponseFailed: ElecChargingPointsSubscriptionCheckInfo = {
    file_name: "test.csv",
    error_count: 2,
    charging_points_count: 0,
    errors: [chargingPointsSubscriptionError1, chargingPointsSubscriptionError2
    ]
}

export const elecChargingPointsSubscriptionCheckResponseSucceed: ElecChargingPointsSubscriptionCheckInfo = {
    file_name: "test.csv",
    error_count: 0,
    charging_points_count: 90
}