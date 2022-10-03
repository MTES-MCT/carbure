import {
  Entity,
  Biofuel,
  Country,
  Feedstock,
  ProductionSite,
} from "carbure/types"
import { Order } from "common/components/table"

export interface SafCertificate {
  id: number
  carbure_id: string
  year: number
  period: number
  date: string | null
  carbure_client: Entity | null
  status: SafCertificateStatus
  total_volume: number
  assigned_volume: number
  assigned_clients: string[]
  feedstock: Feedstock | null
  biofuel: Biofuel | null
  country_of_origin: Country | null
  ghg_reduction: number
}

export interface SafCertificateAssignement {
  volume: number
  carbure_client_id: number
  invoice_reference: string
  date: string
}

export interface SafCertificateDetails extends SafCertificate {
  parent_lot?: LotPreview
  created_at: string
  invoice_reference: string
  carbure_producer: Entity | null
  unknown_producer: string | null
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  production_site_commissioning_date: string | null
  carbure_supplier: Entity | null
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
  ghg_reference: number
}


export interface SafCertificateListResponse {
  saf_certificates: SafCertificate[]
  from: number
  returned: number
  total: number
  ids: number[]
}

export interface SafSnapshot {
  to_assign: number
  to_assign_available: number
  to_assign_history: number
  pending: number
  rejected: number
  accepted: number
}


export interface SafCertificateQuery {
  entity_id: number
  status?: SafCertificateStatus
  year?: number
  query?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  category?: string
  [SafCertificateFilter.Feedstocks]?: string[]
  [SafCertificateFilter.Biofuels]?: string[]
  [SafCertificateFilter.Periods]?: string[]
  [SafCertificateFilter.CountriesOfOrigin]?: string[]
  [SafCertificateFilter.Clients]?: string[]
}

export enum SafCertificateStatus {
  ToAssign = "TO_ASSIGN",
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
}
export enum SafCertificateQueryStatus {
  ToAssign = "to-assign",
  Pending = "pending",
  Accepted = "accepted",
  Rejected = "rejected",
}

export enum SafCertificateFilter {
  Feedstocks = "feedstocks",
  Biofuels = "biofuels",
  Periods = "periods",
  CountriesOfOrigin = "countries_of_origin",
  Clients = "clients",
}

export interface LotPreview {
  id: number
  carbure_id: string
  volume: number
  delivery_date: string
}

export type FilterSelection = Partial<Record<SafCertificateFilter, string[]>>

export interface QueryParams {
  entity: Entity
  year: number
  status: string | undefined
  filters: FilterSelection
  search: string | undefined
  invalid: boolean
  deadline: boolean
  selection: number[]
  page: number
  limit: number | undefined
  order: Order | undefined
  snapshot: SafSnapshot | undefined
}