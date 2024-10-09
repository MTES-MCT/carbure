import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  ProductionSite,
} from "carbure/types"
import {
  CBQueryParams,
  CBQueryStates,
  CBSnapshot,
} from "common/hooks/query-builder-2"
import { SafTicketSourceStatus } from "./pages/operator/types"
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiSafTicketsGetParametersQueryOrder,
  StatusEnum as SafTicketStatus,
} from "api-schema"

export interface SafOperatorSnapshot extends CBSnapshot {
  ticket_sources_available: number
  ticket_sources_history: number
  tickets: number
  tickets_assigned: number
  tickets_assigned_accepted: number
  tickets_assigned_pending: number
  tickets_assigned_rejected: number
  tickets_received: number
  tickets_received_accepted: number
  tickets_received_pending: number
}

export interface SafClientSnapshot extends CBSnapshot {
  tickets_pending: number
  tickets_accepted: number
}

export interface SafLot {
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  volume: number
}

export interface LotPreview {
  id: number
  carbure_id: string
  volume: number
  delivery_date: string
}

export interface SafTicketPreview {
  id: number
  carbure_id: string
  client: string
  volume: number
  status: SafTicketStatus
  created_at: string
}

export type SafTicket = apiTypes["SafTicket"]

export type SafTicketDetails = apiTypes["SafTicketDetails"]

export interface SafProduction {
  carbure_producer: Entity | null
  unknown_producer: string | null
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  production_site_commissioning_date: string
}

export interface SafDurability {
  eec: number
  el: number
  ep: number
  etd: number
  eu: number
  esca: number
  eccs: number
  eccr: number
  eee: number
  ghg_total: number
  ghg_reduction: number
}

export interface SafTicketAssignementQuery {
  volume: number
  client_id: number
  free_field: string
}

// export interface SafTicketsResponse {
//   saf_tickets: SafTicket[]
//   from: number
//   returned: number
//   total: number
//   ids: number[]
// }
export type SafTicketsResponse = apiTypes["PaginatedSafTicketList"]

export interface SafStates extends CBQueryStates {
  //old QueryParams

  status: SafTicketSourceStatus | SafTicketStatus
  filters: SafFilterSelection
  snapshot?: SafOperatorSnapshot | SafClientSnapshot
  type?: SafQueryType
}

export type SafFilterSelection = Partial<Record<SafFilter, string[]>>

export enum SafFilter {
  Feedstocks = "feedstocks",
  Periods = "periods",
  Clients = "clients",
  Suppliers = "suppliers",
  CountriesOfOrigin = "countries_of_origin",
  ProductionSites = "production_sites",
  DeliverySites = "delivery_sites",
}

export type SafQueryType = "assigned" | "received"

export type SafColumsOrder = PathsApiSafTicketsGetParametersQueryOrder
export interface SafQuery extends CBQueryParams<SafColumsOrder[]> {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
}

// Generated enum is EnumStatus and the name is not readable
export { SafTicketStatus }
