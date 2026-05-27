import { cpo } from "common/__test__/data"
import { EntityPreview } from "common/types"
import { ProvisionCertificate, ProvisionCertificateSource } from "../types"

const cpoPreview: EntityPreview = {
  id: cpo.id,
  name: cpo.name,
  entity_type: cpo.entity_type,
  registration_id: cpo.registration_id,
}

export const provisionCertificateMeterReadings: ProvisionCertificate = {
  id: 1,
  cpo: cpoPreview,
  source: ProvisionCertificateSource.METER_READINGS,
  quarter: 1,
  year: 2024,
  date_from: "2024-01-01",
  date_to: "2024-03-31",
  month: "01/2024",
  operating_unit: "UE-001",
  energy_amount: 1250.5,
  created_at: "2024-04-15T10:00:00Z",
  enr_ratio: 0.3,
}

export const provisionCertificateEnrCompensation: ProvisionCertificate = {
  id: 2,
  cpo: cpoPreview,
  source: ProvisionCertificateSource.ENR_RATIO_COMPENSATION,
  quarter: 1,
  year: 2025,
  date_from: null,
  date_to: null,
  month: "",
  operating_unit: "",
  energy_amount: 500,
  created_at: "2024-06-01T10:00:00Z",
  enr_ratio: 0.42,
}
