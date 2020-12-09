import { DepotType, Entity, EntityType } from "common/types"

// ENTITIES

export const producer: Entity = {
  id: 0,
  name: "Producteur Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  national_system_certificate: "",
}

export const trader: Entity = {
  id: 1,
  name: "Trader Test",
  entity_type: EntityType.Trader,
  has_mac: true,
  has_trading: true,
  national_system_certificate: "",
}

export const operator: Entity = {
  id: 2,
  name: "Opérateur Test",
  entity_type: EntityType.Operator,
  has_mac: true,
  has_trading: false,
  national_system_certificate: "",
}

export const admin: Entity = {
  id: 3,
  name: "Admin Test",
  entity_type: EntityType.Administration,
  has_mac: false,
  has_trading: false,
  national_system_certificate: "",
}

// COUNTRIES

export const country = {
  code_pays: "FR",
  name: "France",
  name_en: "France",
  is_in_europe: true,
}

// DELIVERY SITES

export const deliverySite = {
  depot_id: "10",
  name: "Test Delivery Site",
  city: "Test City",
  country: country,
  depot_type: DepotType.Other,
  address: "Test Address",
  postal_code: "64430",
}
