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


export function checkChargingPointsSubscription(entity_id: number, file: File) {

  // const res = api.post<Api<ElecChargingPointsApplicationCheckResponse>>(
  //   "/v5/elec/charging-points/check-application",
  //   { entity_id, file }
  // )
  // return res

  // TO TEST errors
  // return new Promise<ElecChargingPointsApplicationCheckInfo>((resolve) => {
  //   resolve(elecChargingPointsApplicationCheckResponseFailed)
  // })

  // // TO TEST success
  return new Promise<ElecChargingPointsApplicationCheckInfo>((resolve) => {
    resolve(elecChargingPointsApplicationCheckResponseSucceed)
  })


}


export function subscribeChargingPointsApplication(
  entity_id: number,
  file: File,
) {


  // // TO TEST success
  return new Promise((resolve) => {
    resolve(true)
  })

  // // TO TEST error
  // return new Promise((resolve, reject) => {
  //   reject(true)
  // })

  // return api.post("/v5/elec/charging-points/subscription", {
  //   entity_id,
  //   file
  // })
}
