import api, { Api, download } from "common/services/api"
import { ElecChargingPointsApplication, ElecChargingPointsApplicationCheckInfo } from "elec/types"


export function getChargingPointsApplications(entity_id: number, companyId: number) {

  return api.get<Api<ElecChargingPointsApplication[]>>("/v5/elec/charging-points/applications", {
    params: { entity_id, company_id: companyId },
  })
}

export function downloadChargingPointsApplications(entityId: number, companyId: number) {
  return download("/v5/elec/charging-points/applications", { entity_id: entityId, company_id: companyId, export: true })
}

export function checkChargingPointsApplication(entity_id: number, file: File) {
  return api.post<Api<ElecChargingPointsApplicationCheckInfo>>(
    "/v5/elec/charging-points/check-application",
    { entity_id, file }
  )
}

export function downloadChargingPointsApplicationDetails(entityId: number, applicationId: number) {
  return download("/v5/elec/charging-points/application-details", { entity_id: entityId, application_id: applicationId, export: true })
}

export function applyChargingPoints(
  entity_id: number,
  file: File,
) {

  return api.post("/v5/elec/charging-points/add-application", {
    entity_id,
    file
  })

}
