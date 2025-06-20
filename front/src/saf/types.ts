import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  ProductionSite,
} from "common/types"
import {
  CBQueryParams,
  CBQueryStates,
  CBSnapshot,
} from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiSafTicketsGetParametersQueryOrder_by,
  PathsApiSafTicketSourcesGetParametersQueryOrder,
  PathsApiSafTicketSourcesGetParametersQueryStatus as SafTicketSourceSatus,
  PathsApiSafTicketsGetParametersQueryStatus as SafTicketStatus,
  ConsumptionTypeEnum as ConsumptionType,
  PathsApiSafTicketSourcesGetParametersQueryStatus as SafTicketSourceStatus,
} from "api-schema"

// Generated enum is EnumStatus and the name is not readable
export { SafTicketSourceStatus, SafTicketStatus, ConsumptionType }

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

export interface SafStates
  extends CBQueryStates<SafTicketStatus, SafTicketType> {
  filters: SafFilterSelection
  snapshot?: SafSnapshot | SafAirlineSnapshot
}

export type SafTicketOrder = PathsApiSafTicketsGetParametersQueryOrder_by

export interface SafTicketQuery
  extends CBQueryParams<SafTicketOrder[], SafTicketStatus, SafTicketType> {
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
  CountriesOfOrigin = "country_of_origin",
  ProductionSites = "production_site",
  DeliverySites = "delivery_site",
  ConsumptionTypes = "consumption_type",
}

export type SafTicketSourceOrder =
  PathsApiSafTicketSourcesGetParametersQueryOrder

export interface SafTicketSourceQuery
  extends CBQueryParams<
    SafTicketSourceOrder[],
    SafTicketSourceSatus,
    undefined
  > {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: number[]
  [SafFilter.Clients]?: string[]
}

export type SafTicketSource = apiTypes["SafTicketSource"]

export type SafTicketSourceDetails = apiTypes["SafTicketSource"]

export type SafTicketSourcePreview = apiTypes["SafTicketSourcePreview"]
export type SafParentTicketSource = apiTypes["SafParentTicketSource"]
