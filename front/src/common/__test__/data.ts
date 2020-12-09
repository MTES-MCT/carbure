import { Entity, EntityType } from "common/types"

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
  id: 1,
  name: "Opérateur Test",
  entity_type: EntityType.Operator,
  has_mac: true,
  has_trading: false,
  national_system_certificate: "",
}

export const admin: Entity = {
  id: 1,
  name: "Admin Test",
  entity_type: EntityType.Administration,
  has_mac: false,
  has_trading: false,
  national_system_certificate: "",
}
