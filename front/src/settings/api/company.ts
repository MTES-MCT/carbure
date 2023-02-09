import { Unit } from "carbure/types"
import { api } from "common/services/api"

export function toggleMAC(entity_id: number, shouldEnable: boolean) {
  const endpoint = shouldEnable
    ? "/v3/settings/enable-mac"
    : "/v3/settings/disable-mac"
  return api.post(endpoint, { entity_id })
}

export function toggleTrading(entity_id: number, shouldEnable: boolean) {
  const endpoint = shouldEnable
    ? "/v3/settings/enable-trading"
    : "/v3/settings/disable-trading"
  return api.post(endpoint, { entity_id })
}

export function toggleStocks(entity_id: number, shouldEnable: boolean) {
  const endpoint = shouldEnable
    ? "/v3/settings/enable-stocks"
    : "/v3/settings/disable-stocks"
  return api.post(endpoint, { entity_id })
}

export function toggleDirectDeliveries(
  entity_id: number,
  shouldEnable: boolean
) {
  const endpoint = shouldEnable
    ? "/v3/settings/enable-direct-deliveries"
    : "/v3/settings/disable-direct-deliveries"
  return api.post(endpoint, { entity_id })
}

export function updateEntity(
  entity_id: number,
  legal_name: string,
  registration_id: string,
  registered_address: string,
  registered_zipcode: string,
  registered_city: string,
  registered_country: string,
  sustainability_officer: string,
  sustainability_officer_phone_number: string
) {
  return api.post("/v5/settings/update-entity", {
    entity_id,
    legal_name,
    registration_id,
    registered_address,
    registered_zipcode,
    registered_city,
    registered_country,
    sustainability_officer,
    sustainability_officer_phone_number,
  })
}

export function setEntityPreferredUnit(entity_id: number, unit: Unit) {
  return api.post("/set-preferred-unit", { entity_id, unit })
}
