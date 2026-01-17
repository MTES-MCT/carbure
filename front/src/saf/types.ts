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
  PathsApiResourcesAirportsGetParametersQueryShipping_method as SafShippingMethod,
  PathsApiSafTicketsFiltersGetParametersQueryFilter as SafTicketFilter,
  PathsApiSafTicketSourcesFiltersGetParametersQueryFilter as SafTicketSourceFilter,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

// Generated enum is EnumStatus and the name is not readable
export {
  SafTicketSourceStatus,
  SafTicketSourceOrder,
  SafTicketStatus,
  ConsumptionType,
  SafShippingMethod,
  SafTicketFilter,
  SafTicketSourceFilter,
}

export enum SafFilter {
  feedstock = SafTicketSourceFilter.feedstock,
  period = SafTicketSourceFilter.period,
  client = SafTicketSourceFilter.client,
  added_by = SafTicketSourceFilter.added_by,
  country_of_origin = SafTicketSourceFilter.country_of_origin,
  production_site = SafTicketSourceFilter.production_site,
  origin_depot = SafTicketSourceFilter.origin_depot,
  consumption_type = SafTicketFilter.consumption_type,
  reception_airport = SafTicketFilter.reception_airport,
  supplier = SafTicketFilter.supplier,
  client_type = SafTicketFilter.client_type,
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

// Query type builder (exposes state, actions, query type)
export type SafTicketQueryBuilder = QueryBuilder<
  SafTicketStatus,
  SafTicketOrder[]
>

export type SafTicketQuery = SafTicketQueryBuilder["query"] & {
  type: SafTicketType
  [SafTicketFilter.feedstock]?: string[]
  [SafTicketFilter.period]?: number[]
  [SafTicketFilter.client]?: string[]
  [SafTicketFilter.consumption_type]?: ConsumptionType[]
}

export type SafFilterSelection = Partial<Record<SafFilter, string[]>>

export type SafTicketSourceQueryBuilder = QueryBuilder<
  SafTicketSourceStatus,
  SafTicketSourceOrder[]
>

// Utilisé uniquement pour typer la query qui arrive dans api.ts
export type SafTicketSourceQuery = SafTicketSourceQueryBuilder["query"] & {
  [SafTicketSourceFilter.feedstock]?: string[]
  [SafTicketSourceFilter.period]?: number[]
  [SafTicketSourceFilter.client]?: string[]
}

export type SafTicketSource = apiTypes["SafTicketSource"]

export type SafTicketSourceDetails = apiTypes["SafTicketSource"]

export type SafTicketSourcePreview = apiTypes["SafTicketSourcePreview"]
export type SafRelatedTicketSource = apiTypes["SafRelatedTicketSource"]
