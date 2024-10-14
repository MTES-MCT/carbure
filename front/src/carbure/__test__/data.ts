import { CategoryEnum, PreferredUnitEnum } from "api-schema"
import {
  Entity,
  EntityType,
  UserRole,
  DepotType,
  GESOption,
  ProductionSiteDetails,
  Depot,
  User,
  UserRightRequest,
  UserRightStatus,
  UserRight,
  Feedstock,
} from "carbure/types"
import { mergeDeepRight } from "ramda"

// COUNTRIES

export const country = {
  code_pays: "FR",
  name: "France",
  name_en: "France",
  is_in_europe: true,
}

// ENTITIES
export const company: Entity = {
  id: 0,
  name: "Compagnie Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

export const producer: Entity = {
  id: 0,
  name: "Producteur Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

export const trader: Entity = {
  id: 1,
  name: "Trader Test",
  entity_type: EntityType.Trader,
  has_mac: true,
  has_trading: true,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

export const operator: Entity = {
  id: 2,
  name: "Opérateur Test",
  entity_type: EntityType.Op_rateur,
  has_mac: true,
  has_trading: false,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

export const admin: Entity = {
  id: 3,
  name: "Admin Test",
  entity_type: EntityType.Administration,
  has_mac: false,
  has_trading: false,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

export const cpo: Entity = {
  id: 4,
  name: "CPO Test",
  entity_type: EntityType.CPO,
  has_mac: false,
  has_trading: false,
  has_stocks: false,
  has_elec: false,
  has_direct_deliveries: false,
  default_certificate: "",
  legal_name: "",
  registered_address: "",
  registered_country: country,
  registered_zipcode: "",
  registered_city: "",
  registration_id: "",
  sustainability_officer: "",
  sustainability_officer_phone_number: "",
  preferred_unit: PreferredUnitEnum.l,
}

// DELIVERY SITES

export const deliverySite: Depot = {
  depot_id: "10",
  name: "Test Delivery Site",
  city: "Test City",
  country: country,
  depot_type: DepotType.Other,
  address: "Test Address",
  postal_code: "64430",
  electrical_efficiency: null,
  thermal_efficiency: null,
  useful_temperature: null,
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

export const matierePremiere: Feedstock = {
  code: "COLZA",
  name: "Colza",
  name_en: "Colza",
  category: CategoryEnum.CONV,
}

// BIOCARBURANT

export const biocarburant = {
  code: "EMHV",
  name: "EMHV",
}

export const entityRight: UserRight = {
  entity: producer,
  role: UserRole.Admin,
  expiration_date: "",
  date_added: "2020-12-23T16:18:27.233Z",
}

export const entityRequest: UserRightRequest = {
  id: 1,
  user: ["user@company.com"],
  entity: producer,
  date_requested: "2020-12-22T16:18:27.233Z",
  status: UserRightStatus.Accepted,
  comment: "",
  role: UserRole.Admin,
  expiration_date: "",
}

export const entityRights = {
  status: "success",
  data: {
    rights: [entityRight],
    requests: [entityRequest],
  },
}

export const entities = {
  [EntityType.CPO]: cpo,
  [EntityType.Administration]: admin,
  [EntityType.Op_rateur]: operator,
  [EntityType.Trader]: trader,
  [EntityType.Producteur]: producer,
}

type PartialUserParam = Partial<{
  email: User["email"]
  request: Exclude<User["requests"][0], "entity">
  right: Exclude<User["rights"][0], "entity">
}>
type GenerateUserParams = (
  entityType: keyof typeof entities,
  partialUser?: PartialUserParam
) => User

/**
 * This function simplifies the way we mock a user attaching to an entity
 * @param entityType The entity you want to mock
 * @param partialUser Additional informations to overrides default user
 * @returns
 */
export const generateUser: GenerateUserParams = (entityType, partialUser) => {
  const currentEntity = entities[entityType]
  return mergeDeepRight<User, PartialUserParam>(
    {
      email: "user@company.com",
      requests: [
        {
          ...entityRequest,
          entity: currentEntity,
        },
      ],
      rights: [
        {
          ...entityRight,
          entity: currentEntity,
        },
      ],
    },
    {
      ...(partialUser?.email ? { email: partialUser.email } : {}),
      ...(partialUser?.request ? { requests: [partialUser.request] } : {}),
      ...(partialUser?.right ? { rights: [partialUser.right] } : {}),
    }
  )
}
