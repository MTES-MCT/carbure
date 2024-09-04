import { Biofuel, Country, Feedstock } from "carbure/types"
import { operator, producer, productionSite } from "carbure/__test__/data"
import {
  SafTicketSource,
  SafOperatorSnapshot,
  SafTicketSourcesResponse,
  SafTicketsResponse,
  SafTicket,
  SafTicketSourceDetails,
  LotPreview,
  SafTicketPreview,
  SafTicketStatus,
  SafTicketDetails,
  SafClientSnapshot,
} from "saf/types"

export const safOperatorSnapshot: SafOperatorSnapshot = {
  ticket_sources_available: 11,
  ticket_sources_history: 3,
  tickets: 4,
  tickets_assigned: 2,
  tickets_assigned_accepted: 1,
  tickets_assigned_pending: 1,
  tickets_assigned_rejected: 1,
  tickets_received: 2,
  tickets_received_accepted: 1,
  tickets_received_pending: 1,
}

export const safClientSnapshot: SafClientSnapshot = {
  tickets_pending: 2,
  tickets_accepted: 1,
}

export const safClientFilterOptions: string[] = ["Air France", "CORSAIR"]

const feedstock1: Feedstock = {
  code: "LIES_DE_VIN",
  name: "Lies de vin",
  is_double_compte: false,
  category: "ANN-IX-A",
}
const bioduel1: Biofuel = {
  code: "HOC",
  name: "Autres Huiles Hydrotraitées - Kérosène",
}
const country1: Country = {
  code_pays: "FR",
  name: "France",
  name_en: "France",
  is_in_europe: true,
}

export const safTicketSource: SafTicketSource = {
  id: 12343,
  carbure_id: "A12332",
  year: 2022,
  delivery_period: 202201,
  created_at: "2022-02-08",
  total_volume: 10000,
  assigned_volume: 0,
  assigned_tickets: [],
  feedstock: feedstock1,
  biofuel: bioduel1,
  country_of_origin: country1,
  ghg_reduction: 54,
}

export const lotPreview: LotPreview = {
  id: 12345678,
  carbure_id: "12345678",
  volume: 1000,
  delivery_date: "2022-02-08",
}

export const safTicketPreview1: SafTicketPreview = {
  id: 92343,
  carbure_id: "X12332",
  client: "Air France",
  volume: 1000,
  created_at: "2022-01-10",
  status: SafTicketStatus.Rejected,
}

export const safTicketPreview2: SafTicketPreview = {
  id: 92344,
  carbure_id: "X12333",
  client: "CORSAIR",
  volume: 2000,
  created_at: "2022-02-10",
  status: SafTicketStatus.Pending,
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
  biofuel: bioduel1,
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

export const safTicketSource2: SafTicketSource = {
  id: 22343,
  carbure_id: "B21234",
  year: 2022,
  delivery_period: 202202,
  created_at: "2022-01-10",
  assigned_tickets: [safTicketPreview1, safTicketPreview2],
  total_volume: 5000,
  assigned_volume: 2000,
  feedstock: feedstock1,
  biofuel: bioduel1,
  country_of_origin: country1,
  ghg_reduction: 64,
}

export const safTicketSourcesResponse: SafTicketSourcesResponse = {
  saf_ticket_sources: [
    safTicketSource,
    safTicketSource2,
    safTicketSource,
    safTicketSource2,
    safTicketSource2,
    safTicketSource,
    safTicketSource,
    safTicketSource,
    safTicketSource,
    safTicketSource,
    safTicketSource,
  ],
  from: 1,
  returned: 1,
  total: 11,
  ids: [22343, 12343],
}

export const safTicket: SafTicket = {
  id: 12343,
  carbure_id: "A22332",
  year: 2022,
  assignment_period: 202202,
  client: "Air France",
  created_at: "2022-01-10",
  supplier: producer.name,
  volume: 2000,
  feedstock: feedstock1,
  biofuel: bioduel1,
  country_of_origin: country1,
  ghg_reduction: 74,
  status: SafTicketStatus.Pending,
}

export const safTicketAssignedDetails: SafTicketDetails = {
  id: 12343,
  carbure_id: "A22332",
  status: SafTicketStatus.Pending,
  year: 2022,
  assignment_period: 202202,
  client: "Air France",
  created_at: "2022-01-10",
  supplier: producer.name,
  volume: 2000,
  feedstock: feedstock1,
  biofuel: bioduel1,
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
}

// const safTicketSourceSummaryItem: SafTicketSourceSummaryItem = {
//   id: 123,
//   carbure_id: "1E2E2",
//   year: 2022,
//   delivery_period: 202202,
//   total_volume: 3000,
//   feedstock: feedstock1,
//   biofuel: bioduel1,
// }

export const safTicketReceivedDetails: SafTicketDetails = {
  ...safTicketAssignedDetails,
  status: SafTicketStatus.Accepted, // SafTicketStatus.Pending
  client: "TERF SAF",
  // child_ticket_source: { id: 2355, carbure_id: "adada" }
  parent_ticket_source: { id: 2355, carbure_id: "adada" },
}

export const safTicketsResponse: SafTicketsResponse = {
  saf_tickets: [safTicket, safTicket],
  from: 1,
  returned: 1,
  total: 11,
  ids: [12343, 12343],
}
