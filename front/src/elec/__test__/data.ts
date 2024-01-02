import { cpo } from "carbure/__test__/data";
import { EntityPreview, EntityType } from "carbure/types";
import { ChargingPointsApplicationError, ElecChargingPointsApplication, ElecChargingPointsApplicationCheckInfo, ElecChargingPointsApplicationStatus, ElecMeterReadingsApplication, ElecMeterReadingsApplicationCheckInfo, ElecMeterReadingsApplicationStatus, ElecProvisionCertificatePreview, MeterReadingsApplicationError } from "elec/types";
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

//CHARGING POINTS


const elecChargingPointApplication1: ElecChargingPointsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 4,
    charging_point_count: 90,
    power_total: 8,
    application_date: "2023-10-12",
    status: ElecChargingPointsApplicationStatus.Pending,
}

const elecChargingPointApplication2: ElecChargingPointsApplication = {
    id: 2,
    cpo: cpo,
    station_count: 19,
    charging_point_count: 987,
    power_total: 30000,
    application_date: "2023-11-13",
    validation_date: "2023-11-01",
    status: ElecChargingPointsApplicationStatus.Accepted,
}
const elecChargingPointApplication3: ElecChargingPointsApplication = {
    id: 3,
    cpo: cpo,
    station_count: 1,
    charging_point_count: 5,
    power_total: 1000,
    application_date: "2023-09-01",
    status: ElecChargingPointsApplicationStatus.Rejected,
}

export const elecChargingPointsApplications: ElecChargingPointsApplication[] = [
    elecChargingPointApplication1,
    elecChargingPointApplication2,
    elecChargingPointApplication3
]


export const chargingPointsApplicationError1: ChargingPointsApplicationError = {
    line: 12,
    error: "MISSING_CHARGING_POINT_IN_DATAGOUV",
    meta: "8U7Y"
}
export const chargingPointsApplicationError2: ChargingPointsApplicationError = {
    line: 87,
    error: "UNKNOW_ERROR"
}
export const elecChargingPointsApplicationCheckResponseFailed: ElecChargingPointsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 2,
    charging_point_count: 0,
    errors: [chargingPointsApplicationError1, chargingPointsApplicationError2
    ]
}

export const elecChargingPointsApplicationCheckResponseSucceed: ElecChargingPointsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 0,
    charging_point_count: 90
}

// METER READINGS

const elecMeterReadingApplication1: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 4,
    charging_point_count: 90,
    power_total: 8,
    year: 2023,
    quarter: 1,
    application_date: "2023-11-13",

    status: ElecMeterReadingsApplicationStatus.Accepted,
}

const elecMeterReadingApplication2: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 19,
    charging_point_count: 1000,
    power_total: 30000,
    year: 2023,
    quarter: 2,
    application_date: "2023-11-13",

    status: ElecMeterReadingsApplicationStatus.Pending,
}
const elecMeterReadingApplication3: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 19,
    charging_point_count: 1000,
    power_total: 30000,
    year: 2023,
    quarter: 2,
    application_date: "2023-11-13",

    status: ElecMeterReadingsApplicationStatus.Rejected,
}


export const elecMeterReadingsApplications: ElecMeterReadingsApplication[] = [
    elecMeterReadingApplication1,
    elecMeterReadingApplication2,
    elecMeterReadingApplication3
]



export const meterReadingsApplicationError1: MeterReadingsApplicationError = {
    line: 87,
    error: "UNKNOW_ERROR"
}
export const meterReadingsApplicationCheckResponseFailed: ElecMeterReadingsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 1,
    year: 2023,
    quarter: 2,
    charging_point_count: 2,
    errors: [meterReadingsApplicationError1]
}

export const meterReadingsApplicationCheckResponseSuccess: ElecMeterReadingsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 0,
    charging_point_count: 90,
    quarter: 2,
    year: 2023,
    // pending_application_already_exists: true
}