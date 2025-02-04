import { Unit } from "carbure/types"
import { api as apiFetch } from "common/services/api-fetch"

export function toggleMAC(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entities/release-for-consumption/"
  return apiFetch.POST(endpoint, {
    params: { query: { entity_id } },
    body: {
      has_mac: shouldEnable,
    },
  })
}

export function toggleTrading(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entities/trading/"
  return apiFetch.POST(endpoint, {
    params: { query: { entity_id } },
    body: {
      has_trading: shouldEnable,
    },
  })
}
export function toggleElec(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entities/elec/"
  return apiFetch.POST(endpoint, {
    params: { query: { entity_id } },
    body: {
      has_elec: shouldEnable,
    },
  })
}

export function toggleStocks(entity_id: number, shouldEnable: boolean) {
  const endpoint = "/entities/stocks/"
  return apiFetch.POST(endpoint, {
    params: { query: { entity_id } },
    body: {
      has_stocks: shouldEnable,
    },
  })
}

export function toggleDirectDeliveries(
  entity_id: number,
  shouldEnable: boolean
) {
  const endpoint = "/entities/direct-deliveries/"
  return apiFetch.POST(endpoint, {
    params: { query: { entity_id } },
    body: {
      has_direct_deliveries: shouldEnable,
    },
  })
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
  vat_number: string
) {
  return apiFetch.POST("/entities/update-entity-info/", {
    params: { query: { entity_id } },
    body: {
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
      vat_number,
    },
  })
}

export function setEntityPreferredUnit(entity_id: number, unit: Unit) {
  return apiFetch.POST("/entities/unit/", {
    params: { query: { entity_id } },
    body: {
      unit,
    },
  })
}
