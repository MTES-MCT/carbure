import { CategoryEnum, PreferredUnitEnum } from "api-schema"
import {
  Entity,
  EntityType,
  UserRole,
  SiteType,
  GESOption,
  Depot,
  User,
  UserRightRequest,
  UserRightStatus,
  UserRight,
  Feedstock,
  ProductionSite,
  NotificationType,
} from "carbure/types"
import { DeepPartial } from "common/types"
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
  is_enabled: true,
  sustainability_officer_email: "",
  vat_number: "",
  website: "",
  activity_description: "",
  has_saf: false,
  ext_admin_pages: [],
}

export const producer: Entity = {
  ...company,
  id: 1,
  name: "Producteur Test",
  entity_type: EntityType.Producer,
}

export const trader: Entity = {
  ...company,
  id: 2,
  name: "Trader Test",
  entity_type: EntityType.Trader,
}

export const operator: Entity = {
  ...company,
  id: 3,
  name: "Opérateur Test",
  entity_type: EntityType.Operator,
  has_trading: false,
}

export const admin: Entity = {
  ...company,
  id: 4,
  name: "Admin Test",
  entity_type: EntityType.Administration,
  has_mac: false,
  has_trading: false,
}

export const cpo: Entity = {
  ...company,
  id: 5,
  name: "CPO Test",
  entity_type: EntityType.CPO,
  has_mac: false,
  has_trading: false,
}

export const airline: Entity = {
  ...company,
  id: 6,
  name: "Airline Test",
  entity_type: EntityType.Airline,
  has_mac: false,
  has_trading: false,
}

const auditor: Entity = {
  ...company,
  id: 7,
  name: "Auditeur test",
  entity_type: EntityType.Auditor,
  has_mac: false,
  has_trading: false,
}

const powerOrHeatProducer: Entity = {
  ...company,
  id: 8,
  name: "Producteur de chaleur test",
  entity_type: EntityType.PowerOrHeatProducer,
  has_mac: false,
  has_trading: false,
}

export const externalAdmin: Entity = {
  ...admin,
  id: 9,
  name: "External admin",
  entity_type: EntityType.ExternalAdmin,
  has_mac: false,
  has_trading: false,
}

// DELIVERY SITES

export const deliverySite: Depot = {
  id: 1,
  customs_id: "10",
  name: "Test Delivery Site",
  city: "Test City",
  country: country,
  site_type: SiteType.OTHER,
  address: "Test Address",
  postal_code: "64430",
  electrical_efficiency: null,
  thermal_efficiency: null,
  useful_temperature: null,
}

// PRODUCTION SITES

export const productionSite: ProductionSite = {
  name: "Test Production Site",
  country: country,
  id: 2,
  producer: {
    ...producer,
    registered_country: 111,
  },
  date_mise_en_service: "2000-01-31",
  site_siret: "123456",
  address: "",
  postal_code: "64430",
  manager_name: "Bob",
  manager_phone: "012345678",
  manager_email: "bob@bobby.bob",
  ges_option: GESOption.Actual,
  eligible_dc: true,
  dc_reference: "bobobobobob",
  city: "Baigorri",
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
  name_en: "EMHV",
}

export const entityRight: UserRight = {
  entity: producer,
  role: UserRole.Admin,
  name: "Admin Test",
  expiration_date: "",
  email: "test@test.test",
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
  [EntityType.ExternalAdmin]: externalAdmin,
  [EntityType.Operator]: operator,
  [EntityType.Trader]: trader,
  [EntityType.Producer]: producer,
  [EntityType.PowerOrHeatProducer]: powerOrHeatProducer,
  [EntityType.Airline]: airline,
  [EntityType.Auditor]: auditor,
}

type PartialUserParam = DeepPartial<{
  email: User["email"]
  request: User["requests"][0]
  right: User["rights"][0]
}>

/**
 * This function simplifies the way we mock a user attaching to an entity
 * @param entityType The entity you want to mock
 * @param partialUser Additional informations to overrides default user
 * @returns
 */
export const generateUser = (
  entityType: keyof typeof entities,
  partialUser?: PartialUserParam
) => {
  const currentEntity = entities[entityType]

  const res = {
    email: partialUser?.email ?? "user@company.com",
    requests: [
      mergeDeepRight(
        {
          ...entityRequest,
          entity: currentEntity,
        },
        partialUser?.request ?? {}
      ),
    ],
    rights: [
      mergeDeepRight(
        {
          ...entityRight,
          entity: currentEntity,
        },
        partialUser?.right ?? {}
      ),
    ],
  }

  return res
}

export const notifications = [
  {
    id: 1,
    dest: operator,
    datetime: "2024-01-01",
    type: NotificationType.CERTIFICATE_EXPIRED,
    acked: false,
    send_by_email: false,
    email_sent: false,
    meta: {
      certificate: "1234567890",
    },
  },
  {
    id: 2,
    dest: operator,
    datetime: "2024-01-01",
    acked: true,
    send_by_email: false,
    email_sent: false,
    type: NotificationType.LOTS_UPDATED_BY_ADMIN,
    meta: {
      updated: 10,
      comment: "Commentaire de l'admin",
    },
  },
]
