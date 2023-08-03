import {
  Entity,
  EntityType,
  UserRole,
  DepotType,
  GESOption,
  ProductionSiteDetails,
} from "carbure/types"

// ENTITIES
export const company: Entity = {
  id: 0,
  name: "Compagnie Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: "",
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: "l",
}


export const producer: Entity = {
  id: 0,
  name: "Producteur Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: "",
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: "l",
}

export const trader: Entity = {
  id: 1,
  name: "Trader Test",
  entity_type: EntityType.Trader,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: "",
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: "l",
}

export const operator: Entity = {
  id: 2,
  name: "Opérateur Test",
  entity_type: EntityType.Operator,
  has_mac: true,
  has_trading: false,
  has_stocks: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: "",
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: "l",
}

export const admin: Entity = {
  id: 3,
  name: "Admin Test",
  entity_type: EntityType.Administration,
  has_mac: false,
  has_trading: false,
  has_stocks: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: "",
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: "l",
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

export const productionSite: ProductionSiteDetails = {
  name: "Test Production Site",
  country: country,
  id: 2,
  date_mise_en_service: "2000-01-31",
  site_id: "123456",
  address: "",
  postal_code: "64430",
  manager_name: "Bob",
  manager_phone: "012345678",
  manager_email: "bob@bobby.bob",
  ges_option: GESOption.Actual,
  eligible_dc: true,
  dc_reference: "bobobobobob",
  city: "Baigorri",
  inputs: [],
  outputs: [],
  certificates: [],
}

// MATIERE PREMIERE

export const matierePremiere = {
  code: "COLZA",
  name: "Colza",
  category: "CONV",
}

// BIOCARBURANT

export const biocarburant = {
  code: "EMHV",
  name: "EMHV",
}

export const entityRight = {
  name: "User",
  email: "user@company.com",
  entity: producer,
  role: UserRole.Admin,
  expiration_date: null,
}

export const entityRequest = {
  id: 1,
  user: ["user@company.com"],
  entity: producer,
  date_requested: "2020-12-22T16:18:27.233Z",
  status: "ACCEPTED",
  comment: "",
  role: UserRole.Admin,
  expiration_date: null,
}

export const entityRights = {
  status: "success",
  data: {
    rights: [entityRight],
    requests: [entityRequest],
  },
}
