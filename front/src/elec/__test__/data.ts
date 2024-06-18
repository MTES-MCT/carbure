import { cpo } from "carbure/__test__/data";
import { EntityPreview, EntityType } from "carbure/types";
import { ElecApplicationSample } from "elec-audit-admin/types";
import { ChargePointsApplicationError, ElecAuditApplicationStatus, ElecChargePointsApplication, ElecChargePointsApplicationCheckInfo, ElecChargePointsApplicationDetails, ElecMeterReadingsApplication, ElecMeterReadingsApplicationCheckInfo, ElecMeterReadingsApplicationDetails, ElecMeterReadingsApplicationsResponse, ElecProvisionCertificatePreview, MeterReadingsApplicationError, MeterReadingsApplicationUrgencyStatus } from "elec/types";
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
    remaining_energy_amount: 200000,
    current_type: "DC"
}

const elecProvisionCertificatePreview2: ElecProvisionCertificatePreview =
{
    id: 1,
    cpo: elecProvisionCertificateCPOPreview,
    quarter: 1,
    year: 2023,
    operating_unit: "ORIONE",
    energy_amount: 450000,
    remaining_energy_amount: 300000,
    current_type: "AC"

}

export const elecAdminProvisionCertificateList: ElecProvisionCertificatesData = {
    elec_provision_certificates: [elecProvisionCertificatePreview, elecProvisionCertificatePreview2],
    from: 0,
    ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
    returned: 10,
    total: 11
}

//CHARGING POINTS

export const elecAuditApplicationSample: ElecApplicationSample = {
    application_id: 1,
    percentage: 10,
    charge_points: [
        {
            charge_point_id: "FR000028067822",
            longitude: 5.143766000000000,
            latitude: 43.329200000000000
        },
        {
            charge_point_id: "FR000012616553",
            longitude: 43.476584000000000,
            latitude: 5.476711000000000
        }
    ]
}

export const elecChargePointApplicationPending: ElecChargePointsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 4,
    charge_point_count: 90,
    power_total: 8,
    application_date: "2023-10-12",
    status: ElecAuditApplicationStatus.Pending,
}



export const elecChargePointApplicationRejected: ElecChargePointsApplication = {
    id: 3,
    cpo: cpo,
    station_count: 1,
    charge_point_count: 5,
    power_total: 1000,
    application_date: "2023-09-01",
    status: ElecAuditApplicationStatus.Rejected,
}
export const elecChargePointApplicationAuditInProgress: ElecChargePointsApplication = {
    id: 3,
    cpo: cpo,
    station_count: 1,
    charge_point_count: 5,
    power_total: 1000,
    application_date: "2023-09-01",
    audit_order_date: "2023-09-02",
    status: ElecAuditApplicationStatus.AuditInProgress,
}



export const elecChargePointApplicationAuditDone: ElecChargePointsApplication = {
    id: 3,
    cpo: cpo,
    station_count: 1,
    charge_point_count: 5,
    power_total: 1000,
    application_date: "2023-09-01",
    audit_order_date: "2023-09-02",
    status: ElecAuditApplicationStatus.AuditDone,

}

export const elecChargePointApplicationAccepted: ElecChargePointsApplication = {
    id: 2,
    cpo: cpo,
    station_count: 19,
    charge_point_count: 987,
    power_total: 30000,
    application_date: "2023-11-13",
    validation_date: "2023-11-01",
    status: ElecAuditApplicationStatus.Accepted,
}

export const elecChargePointApplicationDetailsPending: ElecChargePointsApplicationDetails = {
    ...elecChargePointApplicationPending,
    email_contacts: ["test1@carbure.com", "test2@carbure.com"]
}

export const elecChargePointApplicationDetailsInProgress: ElecChargePointsApplicationDetails = {
    ...elecChargePointApplicationAuditInProgress,
    email_contacts: ["test1@carbure.com"],
    sample: elecAuditApplicationSample
}


export const elecChargePointsApplications: ElecChargePointsApplication[] = [
    elecChargePointApplicationPending,
    elecChargePointApplicationRejected,
    elecChargePointApplicationAuditInProgress,
    elecChargePointApplicationAuditDone,
    elecChargePointApplicationAccepted,
]


export const chargePointsApplicationError1: ChargePointsApplicationError = {
    line: 12,
    error: "MISSING_CHARGING_POINT_IN_DATAGOUV",
    meta: "8U7Y"
}
export const chargePointsApplicationError2: ChargePointsApplicationError = {
    line: 87,
    error: "UNKNOW_ERROR"
}
export const elecChargePointsApplicationCheckResponseFailed: ElecChargePointsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 2,
    charge_point_count: 0,
    errors: [chargePointsApplicationError1, chargePointsApplicationError2
    ]
}

export const elecChargePointsApplicationCheckResponseSucceed: ElecChargePointsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 0,
    charge_point_count: 90
}

// METER READINGS



const elecMeterReadingApplicationPending: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 19,
    charge_point_count: 1000,
    energy_total: 30000,
    year: 2024,
    quarter: 1,
    application_date: "2024-1-13",
    status: ElecAuditApplicationStatus.Pending,
}

export const elecMeterReadingApplicationDetailsPending: ElecMeterReadingsApplicationDetails = {
    ...elecMeterReadingApplicationPending,
    email_contacts: ["cpo@test.com"],
    power_total: 30000
}

export const elecMeterReadingApplicationAccepted: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 4,
    charge_point_count: 90,
    energy_total: 8,
    year: 2023,
    quarter: 1,
    application_date: "2023-11-13",
    status: ElecAuditApplicationStatus.Accepted,
}
const elecMeterReadingApplicationRejected: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 19,
    charge_point_count: 1000,
    energy_total: 30000,
    year: 2023,
    quarter: 4,
    application_date: "2023-11-13",

    status: ElecAuditApplicationStatus.Rejected,
}
export const elecMeterReadingApplicationAuditInProgress: ElecMeterReadingsApplication = {
    id: 1,
    cpo: cpo,
    station_count: 19,
    charge_point_count: 1000,
    energy_total: 30000,
    year: 2023,
    quarter: 3,
    application_date: "2023-08-13",
    status: ElecAuditApplicationStatus.AuditInProgress,
}


export const elecMeterReadingApplicationDetailsInProgress: ElecMeterReadingsApplicationDetails = {
    ...elecMeterReadingApplicationAuditInProgress,
    email_contacts: ["cpo@test.com"],
    power_total: 30000,
    sample: elecAuditApplicationSample
}

export const elecMeterReadingsApplications: ElecMeterReadingsApplication[] = [
    elecMeterReadingApplicationPending,
    elecMeterReadingApplicationAuditInProgress,
    elecMeterReadingApplicationAccepted,
    elecMeterReadingApplicationRejected,
]



export const elecMeterReadingsApplicationsResponsePending: ElecMeterReadingsApplicationsResponse = {
    applications: [
        elecMeterReadingApplicationPending,
        elecMeterReadingApplicationAccepted,
        elecMeterReadingApplicationRejected
    ],
    current_application: elecMeterReadingApplicationPending,
    current_application_period: {
        quarter: 1,
        year: 2024,
        urgency_status: MeterReadingsApplicationUrgencyStatus.Critical,
        deadline: "2024-04-15"
    }
}

export const elecMeterReadingsApplicationsResponseMissing: ElecMeterReadingsApplicationsResponse = {
    applications: [
        elecMeterReadingApplicationAccepted,
    ],
    current_application: undefined,
    current_application_period: {
        quarter: 1,
        year: 2024,
        // urgency_status: MeterReadingsApplicationUrgencyStatus.Low,
        // urgency_status: MeterReadingsApplicationUrgencyStatus.High,
        urgency_status: MeterReadingsApplicationUrgencyStatus.Critical,
        deadline: "2024-04-15"

    }
}


export const meterReadingsApplicationError1: MeterReadingsApplicationError = {
    line: 87,
    error: "UNKNOW_ERROR"
}
export const meterReadingsApplicationCheckResponseFailed: ElecMeterReadingsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 1,
    year: 2023,
    quarter: 2,
    charge_point_count: 2,
    errors: [meterReadingsApplicationError1]
}

export const meterReadingsApplicationCheckResponseSuccess: ElecMeterReadingsApplicationCheckInfo = {
    file_name: "test.csv",
    error_count: 0,
    charge_point_count: 90,
    quarter: 2,
    year: 2023,
    // pending_application_already_exists: true
}