import api, { Api } from "common/services/api"
import { elecChargingPointsApplicationCheckResponseFailed, elecChargingPointsApplicationCheckResponseSucceed, elecChargingPointsApplications } from "elec/__test__/data"
import { ElecChargingPointsApplication, ElecChargingPointsApplicationCheckInfo } from "elec/types"



export function getChargingPointsApplications(entity_id: number) {

  // TO TEST without data
  return new Promise<ElecChargingPointsApplication[]>((resolve) => {
    resolve(elecChargingPointsApplications)
  })

  // return api.get<Api<ElecChargingPointsApplication[]>>("/v5/elec/charging-points/applications", {
  //   params: { entity_id },
  // })
}


export function checkChargingPointsApplication(entity_id: number, file: File) {

  // TO TEST errors
  // return new Promise<ElecChargingPointsApplicationCheckInfo>((resolve) => {
  //   resolve(elecChargingPointsApplicationCheckResponseFailed)
  // })

  // // TO TEST success
  return new Promise<ElecChargingPointsApplicationCheckInfo>((resolve) => {
    resolve(elecChargingPointsApplicationCheckResponseSucceed)
  })

  // const res = api.post<Api<ElecChargingPointsApplicationCheckResponse>>(
  //   "/v5/elec/charging-points/check-file",
  //   { entity_id, file }
  // )
  // return res
}


export function addChargingPointsApplication(
  entity_id: number,
  file: File,
) {

  return api.post("/v5/elec/charging-points/add", {
    entity_id,
    file
  })
}
