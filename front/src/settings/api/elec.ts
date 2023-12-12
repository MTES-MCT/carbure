import api, { Api, download } from "common/services/api"
import { ElecChargingPointsApplication, ElecChargingPointsApplicationCheckInfo } from "elec/types"


export function getChargingPointsApplications(entity_id: number, companyId: number) {

  return api.get<Api<ElecChargingPointsApplication[]>>("/elec/cpo/charging-points/applications", {
    params: { entity_id, company_id: companyId },
  })
}

export function downloadChargingPoints(entityId: number, companyId: number) {
  return download("/elec/cpo/charging-points", { entity_id: entityId, company_id: companyId, export: true })
}

export function checkChargingPointsApplication(entity_id: number, file: File) {
  return api.post<Api<ElecChargingPointsApplicationCheckInfo>>(
    "/elec/cpo/charging-points/check-application",
    { entity_id, file }
  )
}

export function downloadChargingPointsApplicationDetails(entityId: number, applicationId: number) {
  return download("/elec/cpo/charging-points/application-details", { entity_id: entityId, application_id: applicationId, export: true })
}

export function applyChargingPoints(
  entity_id: number,
  file: File,
) {

  return api.post("/elec/cpo/charging-points/add-application", {
    entity_id,
    file
  })

}
