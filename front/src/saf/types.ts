import {
  Entity,
  Biofuel,
  Country,
  Feedstock,
  ProductionSite,
} from "carbure/types"
import { Order } from "common/components/table"

export interface SafOperatorSnapshot {
  ticket_sources_available: number
  ticket_sources_history: number
  tickets: number
  tickets_pending: number,
  tickets_rejected: number,
  tickets_accepted: number,
}

export interface SafClientSnapshot {
  tickets_pending: number,
  tickets_accepted: number,
}

export interface SafTicketSource {
  id: number
  carbure_id: string
  year: number
  period: number
  created_at: string
  total_volume: number
  assigned_volume: number
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  assigned_tickets: SafTicketPreview[]
  ghg_reduction: number // attention pour les lots c'etait ghg_reduction_red_ii
}

export interface SafTicketSourceDetails extends SafTicketSource, SafProduction, SafDurability {
  parent_lot?: LotPreview
  added_by: Entity,

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
  period: number
  created_at: string
  supplier: string
  client: string
  volume: number
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  ghg_reduction: number // attention pour les lots c'etait ghg_reduction_red_ii
  status: SafTicketStatus
}

export interface SafTicketDetails extends SafTicket, SafProduction, SafDurability {
  // parent_ticket_source?: SafTicketSource TODO on a vraiment besoin de ça ? ce n'est pas visible sur les maquettes
  free_field?: string
  client_comment?: string
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

export interface SafQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  [SafFilter.Feedstocks]?: string[]
  [SafFilter.Periods]?: string[]
  [SafFilter.Clients]?: string[]
}

export interface SafTicketSourcesResponse {
  saf_ticket_sources: SafTicketSource[]
  from: number
  returned: number
  total: number
  ids: number[]
}

export interface SafTicketsResponse {
  saf_tickets: SafTicket[]
  from: number
  returned: number
  total: number
  ids: number[]
}

export enum SafTicketSourceStatus {
  Available = "available",
  History = "history",
}

export interface SafStates { //old QueryParams
  entity: Entity
  year: number
  status: SafTicketSourceStatus | SafTicketStatus
  filters: SafFilterSelection
  search?: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: SafOperatorSnapshot | SafClientSnapshot
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
  Supplier = "suppliers",
}