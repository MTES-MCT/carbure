import { Biofuel, Country, Entity, Feedstock } from "carbure/types"
import { LotPreview, SafDurability, SafProduction, SafTicketPreview } from "saf/types"


export enum SafTicketSourceStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export interface SafTicketSource {
  id: number
  carbure_id: string
  year: number
  delivery_period: number
  created_at: string
  total_volume: number
  assigned_volume: number
  feedstock: Feedstock
  biofuel: Biofuel
  country_of_origin: Country
  assigned_tickets: SafTicketPreview[]
  ghg_reduction: number // attention pour les lots c'etait ghg_reduction_red_ii
  parent_lot?: {
    id: number
    carbure_id: string
  }
}

export interface SafTicketSourceSummary
  extends SafTicketSource,
  SafProduction,
  SafDurability {
  count: number
  total_volume: number
  ticket_sources: SafTicketSourceSummaryItem[]
}



export interface SafTicketSourceDetails
  extends SafTicketSource,
  SafProduction,
  SafDurability {
  added_by: Entity
  parent_lot: LotPreview
}

export interface SafTicketSourcesResponse {
  saf_ticket_sources: SafTicketSource[]
  from: number
  returned: number
  total: number
  ids: number[]
}


export interface SafTicketSourceSummaryItem extends SafTicketSourcePreview {
  year: number
  delivery_period: number
  total_volume: number
  feedstock: Feedstock
  biofuel: Biofuel
}

export interface SafTicketSourcePreview {
  id: number
  carbure_id: string
}
