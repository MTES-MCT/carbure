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

// PRODUCTION SITES

export const productionSite = {
  name: "Test Production Site",
  country: country,
  id: 2,
  date_mise_en_service: "2000-01-31",
  site_id: "123456",
  postal_code: "64430",
  manager_name: "Bob",
  manager_phone: "012345678",
  manager_email: "bob@bobby.bob",
  ges_option: "Actual",
  eligible_dc: true,
  dc_reference: "bobobobobob",
  city: "Baigorri",
  inputs: [],
  outputs: [],
  certificates: [],
}

// ISCC CERTIFICATES

export const isccCertificate = {
  certificate_id: "ISCC Test",
  certificate_holder: "Holder Test",
  valid_from: "2020-04-25",
  valid_until: "2021-04-24",
  issuing_cb: "Authority Test",
  location: "",
  scope: ["Scope Test"],
}

export const expiredISCCCertificate = {
  certificate_id: "Expired ISCC Test",
  certificate_holder: "Expired Holder Test",
  valid_from: "1990-01-01",
  valid_until: "2000-01-01",
  issuing_cb: "Expired Authority Test",
  location: "",
  scope: ["Expired Scope Test"],
}

export const dbsCertificate = {
  certificate_id: "2BS Test",
  certificate_holder: "Holder Test",
  holder_address: "Address Test",
  valid_from: "2020-04-25",
  valid_until: "2021-04-24",
  certification_type: "",
  download_link: "",
  scope: ["Scope Test"],
  has_been_updated: false,
}

export const expired2BSCertificate = {
  certificate_id: "Expired 2BS Test",
  certificate_holder: "Expired Holder Test",
  holder_address: "Expired Address Test",
  valid_from: "1990-01-01",
  valid_until: "2000-01-01",
  certification_type: "",
  download_link: "",
  scope: ["Expired Scope Test"],
  has_been_updated: false,
}
