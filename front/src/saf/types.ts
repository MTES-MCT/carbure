import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  ProductionSite,
} from "common/types"
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiSafTicketsGetParametersQueryOrder_by,
  PathsApiSafTicketSourcesGetParametersQueryOrder_by as SafTicketSourceOrder,
  PathsApiSafTicketsGetParametersQueryStatus as SafTicketStatus,
  PathsApiSafTicketsGetParametersQueryConsumption_type as ConsumptionType,
  PathsApiSafTicketSourcesGetParametersQueryStatus as SafTicketSourceStatus,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

// Generated enum is EnumStatus and the name is not readable
export {
  SafTicketSourceStatus,
  SafTicketSourceOrder,
  SafTicketStatus,
  ConsumptionType,
}

// SafSnapshot query returns two possible objects, one for airline entity, one for operator
export interface SafSnapshot {
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

export interface SafLot {
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  volume: number
}

export type LotPreview = apiTypes["CarbureLotPublic"]

export type SafTicketPreview = apiTypes["SafTicketPreview"]
export type SafAssignedTicket = apiTypes["SafAssignedTicket"]

export type SafTicket = apiTypes["SafTicket"]

export type SafTicketDetails = apiTypes["SafTicket"]

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

export type SafTicketsResponse = apiTypes["PaginatedSafTicketPreviewList"]

export type SafTicketType = "assigned" | "received"

export type SafTicketOrder = PathsApiSafTicketsGetParametersQueryOrder_by

// export interface SafStates
//   extends CBQueryStates<SafTicketStatus, SafTicketType> {
//   filters: SafFilterSelection
//   snapshot?: SafSnapshot
// }
// export interface SafTicketQuery
//   extends CBQueryParams<SafTicketOrder[], SafTicketStatus, SafTicketType> {
//   [SafFilter.Feedstocks]?: string[]
//   [SafFilter.Periods]?: number[]
//   [SafFilter.Clients]?: string[]
//   [SafFilter.ConsumptionTypes]?: ConsumptionType[]
// }

// Query type builder (exposes state, actions, query type)
export type SafTicketQueryBuilder = QueryBuilder<
  SafTicketStatus,
  SafTicketOrder[]
>

export type SafTicketQuery = SafTicketQueryBuilder["query"] & {
  type: SafTicketType
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
  [SafFilter.ConsumptionTypes]?: ConsumptionType[]
}

export type SafFilterSelection = Partial<Record<SafFilter, string[]>>

export enum SafFilter {
  Feedstocks = "feedstock",
  Periods = "period",
  Clients = "client",
  Suppliers = "supplier",
  AddedBy = "added_by",
  Airport = "reception_airport",
  CountriesOfOrigin = "country_of_origin",
  ProductionSites = "production_site",
  DeliverySites = "delivery_site",
  ConsumptionTypes = "consumption_type",
}

// export type SafTicketQueryBuilder = QueryBuilder<
//   SafTicketStatus,
//   SafTicketOrder[]
// >

// export type SafTicketQuery = SafTicketQueryBuilder["query"] & {
//   type: SafTicketType
//   [SafFilter.Feedstocks]?: string[]
//   [SafFilter.Periods]?: number[]
//   [SafFilter.Clients]?: string[]
//   [SafFilter.ConsumptionTypes]?: ConsumptionType[]
// }

export type SafTicketSourceQueryBuilder = QueryBuilder<
  SafTicketSourceStatus,
  SafTicketSourceOrder[]
>

// Utilisé uniquement pour typer la query qui arrive dans api.ts
export type SafTicketSourceQuery = SafTicketSourceQueryBuilder["query"] & {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
}

export type SafTicketSource = apiTypes["SafTicketSource"]

export type SafTicketSourceDetails = apiTypes["SafTicketSource"]

export type SafTicketSourcePreview = apiTypes["SafTicketSourcePreview"]
export type SafRelatedTicketSource = apiTypes["SafRelatedTicketSource"]
