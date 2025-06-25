import {
  company,
  deliverySite,
  operator,
  producer,
  productionSite,
  trader,
} from "common/__test__/data"
import {
  Airport,
  Biofuel,
  CategoryEnum,
  Country,
  EntityType,
  Feedstock,
} from "common/types"
import {
  LotPreview,
  SafAssignedTicket,
  SafSnapshot,
  SafTicketDetails,
  SafTicketPreview,
  SafTicketSourcePreview,
  SafTicketsResponse,
  SafTicketStatus,
  SafTicketSourceDetails,
} from "saf/types"
import { SiteTypeEnum } from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export const safOperatorSnapshot: SafSnapshot = {
  ticket_sources_available: 11,
  ticket_sources_history: 3,
  tickets_assigned: 2,
  tickets_assigned_accepted: 1,
  tickets_assigned_pending: 1,
  tickets_assigned_rejected: 1,
  tickets_received: 2,
  tickets_received_accepted: 1,
  tickets_received_pending: 1,
}

export const safClientFilterOptions: string[] = ["Air France", "CORSAIR"]

const feedstock1: Feedstock = {
  code: "LIES_DE_VIN",
  name: "Lies de vin",
  name_en: "Lies de vin",
  is_double_compte: false,
  category: CategoryEnum.ANN_IX_A,
}
const biofuel1: Biofuel = {
  code: "HOC",
  name: "Autres Huiles Hydrotraitées - Kérosène",
  name_en: "Autres Huiles Hydrotraitées - Kérosène",
}
const country1: Country = {
  code_pays: "FR",
  name: "France",
  name_en: "France",
  is_in_europe: true,
}

const safAirport: Airport = {
  id: 12,
  name: "Airport",
  city: "Paris",
  icao_code: "ABCD",
  country: country1,
  site_type: SiteTypeEnum.AIRPORT,
  address: "Rue de l'aéroport",
  postal_code: "75000",
}

export const safTicketSource: SafTicketSourcePreview = {
  id: 12343,
  carbure_id: "A12332",
  year: 2022,
  delivery_period: 202201,
  created_at: "2022-02-08",
  total_volume: 10000,
  assigned_volume: 0,
  assigned_tickets: [],
  feedstock: feedstock1,
  biofuel: biofuel1,
  country_of_origin: country1,
  ghg_reduction: 54,
  parent_lot: {
    id: 1,
    carbure_id: "1",
  },
  parent_ticket: undefined,
}

export const lotPreview: LotPreview = {
  id: 12345678,
  carbure_id: "12345678",
  volume: 1000,
  delivery_date: "2022-02-08",
  added_by: operator,
  biofuel: biofuel1,
  carbure_client: company,
  carbure_delivery_site: deliverySite,
  year: 2022,
  carbure_dispatch_site: deliverySite,
  carbure_producer: producer,
  carbure_production_site: productionSite,
  carbure_supplier: trader,
  carbure_vendor: trader,
  country_of_origin: country1,
  period: 4,
  created_at: "2022-02-07",
  delivery_site_country: country1,
  dispatch_site_country: country1,
  feedstock: feedstock1,
  production_country: country1,
}

export const safTicketPreview1: SafAssignedTicket = {
  id: 92343,
  carbure_id: "X12332",
  client: "Air France",
  volume: 1000,
  created_at: "2022-01-10",
  status: SafTicketStatus.REJECTED,
  assignment_period: 202401,
}

export const safTicketPreview2: SafAssignedTicket = {
  id: 92344,
  carbure_id: "X12333",
  client: "CORSAIR",
  volume: 2000,
  created_at: "2022-02-10",
  status: SafTicketStatus.PENDING,
  assignment_period: 202401,
}

export const safTicketSourceDetails: SafTicketSourceDetails = {
  id: 12343,
  carbure_id: "A12332",
  year: 2022,
  delivery_period: 202201,
  created_at: "2022-02-08",
  total_volume: 5000,
  assigned_volume: 3000,
  feedstock: feedstock1,
  biofuel: biofuel1,
  country_of_origin: country1,
  ghg_reduction: 54,
  parent_lot: lotPreview,
  added_by: operator,
  assigned_tickets: [safTicketPreview1, safTicketPreview2], //[],//
  carbure_producer: producer,
  unknown_producer: "",
  carbure_production_site: productionSite,
  unknown_production_site: "",
  production_site_commissioning_date: "2000-01-31",
  eec: 14.5,
  el: 0,
  ep: 7,
  etd: 2,
  eu: 0,
  esca: 0,
  eccs: 0,
  eccr: 0,
  eee: 0,
  ghg_total: 23.5,
}

export const safTicketSource2: SafTicketSourcePreview = {
  id: 22343,
  carbure_id: "B21234",
  year: 2022,
  delivery_period: 202202,
  created_at: "2022-01-10",
  assigned_tickets: [safTicketPreview1, safTicketPreview2],
  total_volume: 5000,
  assigned_volume: 2000,
  feedstock: feedstock1,
  biofuel: biofuel1,
  country_of_origin: country1,
  ghg_reduction: 64,
  parent_lot: {
    id: 1,
    carbure_id: "1",
  },
}

export const safTicket: SafTicketPreview = {
  id: 12343,
  carbure_id: "A22332",
  year: 2022,
  assignment_period: 202202,
  client: "Air France",
  supplier: producer.name,
  volume: 2000,
  feedstock: feedstock1,
  biofuel: biofuel1,
  country_of_origin: country1,
  ghg_reduction: 74,
  status: SafTicketStatus.PENDING,
  created_at: "2022-02-08",
}

export const safTicketAssignedDetails: SafTicketDetails = {
  id: 12343,
  carbure_id: "A22332",
  status: SafTicketStatus.PENDING,
  year: 2022,
  assignment_period: 202202,
  client: "Air France",
  created_at: "2022-01-10",
  supplier: producer.name,
  volume: 2000,
  feedstock: feedstock1,
  biofuel: biofuel1,
  country_of_origin: country1,
  client_comment: "C'eest vraiment n'importe quoi !",
  ghg_reduction: 74,
  carbure_producer: producer,
  unknown_producer: "",
  carbure_production_site: productionSite,
  unknown_production_site: "",
  production_site_commissioning_date: "2000-01-31",
  eec: 14.5,
  el: 0,
  ep: 7,
  etd: 2,
  eu: 0,
  esca: 0,
  eccs: 0,
  eccr: 0,
  eee: 0,
  ghg_total: 23.5,
  parent_ticket_source: safTicketSource,
  reception_airport: safAirport,
  child_ticket_sources: [],
}

export const safTicketReceivedDetails: SafTicketDetails = {
  ...safTicketAssignedDetails,
  status: SafTicketStatus.ACCEPTED, // SafTicketStatus.PENDING
  client: "TERF SAF",
  parent_ticket_source: safTicketSource,
}

export const safTicketsResponse: SafTicketsResponse = {
  count: 2,
  results: [safTicket, safTicket],
}

export const safClients: apiTypes["EntityPreview"][] = [
  {
    id: 1,
    name: "Compagnie aérienne 1",
    entity_type: EntityType.Airline,
  },
  {
    id: 2,
    name: "Compagnie aérienne 2",
    entity_type: EntityType.Airline,
  },
  {
    id: 3,
    name: "Opérateur 1",
    entity_type: EntityType.Operator,
  },
  {
    id: 4,
    name: "Opérateur 2",
    entity_type: EntityType.Operator,
  },
]
