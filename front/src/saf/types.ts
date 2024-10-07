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
} from "common/hooks/query-builder"
import {
  SafTicketSourcePreview,
  SafTicketSourceStatus,
} from "./pages/operator/types"

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

export interface SafTicket {
  id: number
  carbure_id: string
  year: number
  assignment_period: number
  created_at: string
  supplier: string
  client: string
  volume: number
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  ghg_reduction: number
  status: SafTicketStatus
}

export interface SafTicketDetails
  extends SafTicket,
    SafProduction,
    SafDurability {
  free_field?: string
  client_comment?: string
  // child_ticket_source?: {
  //   id: number
  //   carbure_id: string
  // },
  parent_ticket_source?: SafTicketSourcePreview
}

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

export interface SafTicketsResponse {
  saf_tickets: SafTicket[]
  from: number
  returned: number
  total: number
  ids: number[]
}

export interface SafStates extends CBQueryStates {
  //old QueryParams

  status: SafTicketSourceStatus | SafTicketStatus
  filters: SafFilterSelection
  snapshot?: SafOperatorSnapshot | SafClientSnapshot
  type?: SafQueryType
}

export type SafFilterSelection = Partial<Record<SafFilter, string[]>>

export enum SafTicketStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
}

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

export interface SafQuery extends CBQueryParams {
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: string[]
  [SafFilter.Clients]?: string[]
}
