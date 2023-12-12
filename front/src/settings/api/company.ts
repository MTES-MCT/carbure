import { Unit } from "carbure/types"
import { api } from "common/services/api"

export function toggleMAC(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entity/options/release-for-consumption"
  return api.post(endpoint, { entity_id, has_mac: shouldEnable })
}

export function toggleTrading(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entity/options/trading"
  return api.post(endpoint, { entity_id, has_trading: shouldEnable })
}
export function toggleElec(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entity/options/elec"
  return api.post(endpoint, { entity_id, has_elec: shouldEnable })
}

export function toggleStocks(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entity/options/stocks"
  return api.post(endpoint, { entity_id, has_stocks: shouldEnable })
}

export function toggleDirectDeliveries(
  entity_id: number,
  shouldEnable: boolean
) {
  const endpoint = "/entity/options/direct-deliveries"
  return api.post(endpoint, { entity_id, has_direct_deliveries: shouldEnable })
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
  return api.post("/entity/update-info", {
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
  return api.post("/entity/options/unit", { entity_id, unit })
}
