import api, { Api } from "common/services/api"
import { elecChargingPointsSubscriptionCheckResponseSucceed, elecChargingPointsSubscriptions } from "elec/__test__/data"
import { ElecChargingPointsSubscription, ElecChargingPointsSubscriptionCheckInfo } from "elec/types"



export function getChargingPointsSubscriptions(entity_id: number) {

  // TO TEST without data
  return new Promise<ElecChargingPointsSubscription[]>((resolve) => {
    resolve(elecChargingPointsSubscriptions)
  })

  // return api.get<Api<ElecChargingPointsSubscription[]>>("/v5/elec/charging-points/subscription", {
  //   params: { entity_id },
  // })
}


export function checkChargingPointsSubscription(entity_id: number, file: File) {

  // const res = api.post<Api<ElecChargingPointsSubscriptionCheckResponse>>(
  //   "/v5/elec/charging-points/check-subscription",
  //   { entity_id, file }
  // )
  // return res

  // TO TEST errors
  // return new Promise<ElecChargingPointsSubscriptionCheckInfo>((resolve) => {
  //   resolve(elecChargingPointsSubscriptionCheckResponseFailed)
  // })

  // // TO TEST success
  return new Promise<ElecChargingPointsSubscriptionCheckInfo>((resolve) => {
    resolve(elecChargingPointsSubscriptionCheckResponseSucceed)
  })


}


export function subscribeChargingPoints(
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
