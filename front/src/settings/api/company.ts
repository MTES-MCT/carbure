import { EntityType, Unit } from "carbure/types"
import { api } from "common/services/api"
import { Certificate } from "crypto"

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
  activity_description: string,
  legal_name: string,
  registered_address: string,
  registered_city: string,
  registered_country_code: string,
  registered_zipcode: string,
  registration_id: string,
  sustainability_officer_email: string,
  sustainability_officer_phone_number: string,
  sustainability_officer: string,
  website: string,
  vat_number: string,
) {

  return api.post("/entity/update-info", {
    entity_id,
    activity_description,
    legal_name,
    registered_address,
    registered_city,
    registered_country_code,
    registered_zipcode,
    registration_id,
    sustainability_officer_email,
    sustainability_officer_phone_number,
    sustainability_officer,
    website,
    vat_number
  })
}




export function setEntityPreferredUnit(entity_id: number, unit: Unit) {
  return api.post("/entity/options/unit", { entity_id, unit })
}
