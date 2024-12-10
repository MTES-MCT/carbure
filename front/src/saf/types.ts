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
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiSafTicketsGetParametersQueryOrder,
  PathsApiSafTicketSourcesGetParametersQueryOrder,
  PathsApiSafTicketSourcesGetParametersQueryStatus as SafTicketSourceSatus,
  PathsApiSafTicketsGetParametersQueryStatus as SafTicketStatus,
} from "api-schema"

// SafSnapshot query returns two possible objects, one for airline entity, one for operator
export interface SafOperatorSnapshot {
  ticket_sources_available: number
  ticket_sources_history: number
  tickets_assigned: number
  tickets_assigned_accepted: number
  tickets_assigned_pending: number
  tickets_assigned_rejected: number
  tickets_received: number
  tickets_received_accepted: number
  tickets_received_pending: number
}

export interface SafAirlineSnapshot extends CBSnapshot {
  tickets_pending: number
  tickets_accepted: number
}

export interface SafLot {
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  volume: number
}

export type LotPreview = apiTypes["CarbureLotPublic"]

export type SafTicketPreview = apiTypes["SafTicketPreview"]

export type SafTicket = apiTypes["SafTicket"]

export type SafTicketDetails = apiTypes["SafTicketDetails"]

export interface SafProduction {
  carbure_producer: Entity | null
  unknown_producer: string | null
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  production_site_commissioning_date: string
}

export type SafDurability = Pick<
  SafTicketDetails,
  | "eec"
  | "el"
  | "ep"
  | "etd"
  | "eu"
  | "esca"
  | "eccs"
  | "eccr"
  | "eee"
  | "ghg_total"
  | "ghg_reduction"
>

export interface SafTicketAssignementQuery {
  volume: number
  client_id: number
  free_field: string
}

export type SafTicketsResponse = apiTypes["PaginatedSafTicketList"]

export interface SafStates
  extends CBQueryStates<SafTicketStatus, SafQueryType> {
  filters: SafFilterSelection
  snapshot?: SafOperatorSnapshot | SafAirlineSnapshot
}

export interface SafQuery
  extends CBQueryParams<SafColumsOrder[], SafTicketStatus, SafQueryType> {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
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

// Airline
export type SafColumsOrder = PathsApiSafTicketsGetParametersQueryOrder

// Operator
export type SafOperatorColumnsOrder =
  PathsApiSafTicketSourcesGetParametersQueryOrder
export interface SafOperatorQuery
  extends CBQueryParams<
    SafOperatorColumnsOrder[],
    SafTicketSourceSatus,
    undefined
  > {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
}

// Generated enum is EnumStatus and the name is not readable
export { SafTicketStatus }
