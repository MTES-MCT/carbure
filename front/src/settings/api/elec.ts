import api, { Api, download } from "common/services/api"
import { ElecChargingPointsSubscription, ElecChargingPointsSubscriptionCheckInfo } from "elec/types"


export function getChargingPointsSubscriptions(entity_id: number, companyId: number) {

  return api.get<Api<ElecChargingPointsSubscription[]>>("/v5/elec/charging-points/subscriptions", {
    params: { entity_id, company_id: companyId },
  })
}

export function downloadChargingPointsSubscriptions(entityId: number, companyId: number) {
  return download("/v5/elec/charging-points/subscriptions", { entity_id: entityId, company_id: companyId, export: true })
}

export function checkChargingPointsSubscription(entity_id: number, file: File) {
  return api.post<Api<ElecChargingPointsSubscriptionCheckInfo>>(
    "/v5/elec/charging-points/check-subscription",
    { entity_id, file }
  )
}

export function downloadChargingPointsSubscriptionDetails(entityId: number, subscriptionId: number) {
  return download("/v5/elec/charging-points/subscription-details", { entity_id: entityId, subscription_id: subscriptionId, export: true })
}

export function subscribeChargingPoints(
  entity_id: number,
  file: File,
) {

  return api.post("/v5/elec/charging-points/add-subscription", {
    entity_id,
    file
  })

}
