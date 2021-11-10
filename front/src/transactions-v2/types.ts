import { Option } from "common-v2/hooks/normalize"
import {
  Biofuel,
  Country,
  Depot,
  Entity,
  Feedstock,
  ProductionSite,
} from "common/types"

export interface Lot {
  id: number
  year: number
  period: number
  carbure_id: string
  carbure_producer: Entity | null
  unknown_producer: string | null
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  production_country: Country | null
  production_site_commissioning_date: string | null
  production_site_certificate: string | null
  production_site_double_counting_certificate: string | null
  carbure_supplier: Entity | null
  unknown_supplier: string | null
  supplier_certificate: string | null
  supplier_certificate_type: string | null
  transport_document_type: TransportDocumentType
  transport_document_reference: string | null
  carbure_client: Entity | null
  unknown_client: string | null
  dispatch_date: string | null
  carbure_dispatch_site: Depot | null
  unknown_dispatch_site: string | null
  delivery_date: string | null
  carbure_delivery_site: Depot | null
  unknown_delivery_site: string | null
  delivery_site_country: Country | null
  delivery_type: DeliveryType
  lot_status: LotStatus
  correction_status: CorrectionStatus
  volume: number
  weight: number
  lhv_amount: number
  feedstock: Feedstock | null
  biofuel: Biofuel | null
  country_of_origin: Country | null
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
  ghg_reduction: number
  ghg_reference_red_ii: number
  ghg_reduction_red_ii: number
  free_field: string
}

export interface LotList {
  lots: Lot[]
}

export interface Snapshot {
  lots: {
    draft: number
    in_total: number
    in_pending: number
    in_accepted: number
    in_tofix: number
    stock: number
    out_total: number
    out_pending: number
    out_accepted: number
    out_tofix: number
  }
}

export enum LotStatus {
  Draft = "DRAFT",
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
  Frozen = "FROZEN",
  Deleted = "DELETED",
}

export enum CorrectionStatus {
  NoProblem = "NO_PROBLEMO",
  InCorrection = "IN_CORRECTION",
  Fixed = "FIXED",
}

export enum DeliveryType {
  Unknown = "UNKNOWN",
  RFC = "RFC", // release for consumption / mise a consommation
  Stock = "STOCK",
  Blending = "BLENDING", // incorporation
  Export = "EXPORT",
  Trading = "TRADING",
  Processing = "PROCESSING",
  Direct = "DIRECT", // livraison directe
}

export enum TransportDocumentType {
  DAU = "DAU",
  DAE = "DAE",
  DSA = "DSA",
  DSAC = "DSAC",
  DSP = "DSP",
  Other = "OTHER",
}

export enum Filter {
  DeliveryStatus = "delivery_status",
  Feedstocks = "feedstocks",
  Biofuels = "biofuels",
  Periods = "periods",
  CountriesOfOrigin = "countries_of_origin",
  Suppliers = "suppliers",
  Clients = "clients",
  ProductionSites = "production_sites",
  DeliverySites = "delivery_sites",
  AddedBy = "added_by",
  Errors = "errors",
  Forwarded = "is_forwarded",
  Mac = "is_mac",
  HiddenByAdmin = "is_hidden_by_admin",
  HiddenByAuditor = "is_hidden_by_auditor",
  ClientTypes = "client_types",
  ShowEmpty = "show_empty",
}

export type FilterSelection = Partial<Record<Filter, Option[]>>

export interface LotQuery {
  entity_id: number
  status?: string // "draft" | "in" | "stock" | "out"
  year?: number
  search?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  invalid?: boolean
  deadline?: boolean
  history?: boolean
  correction?: boolean
  [Filter.DeliveryStatus]?: string[]
  [Filter.Feedstocks]?: string[]
  [Filter.Biofuels]?: string[]
  [Filter.Periods]?: string[]
  [Filter.CountriesOfOrigin]?: string[]
  [Filter.Suppliers]?: string[]
  [Filter.Clients]?: string[]
  [Filter.ProductionSites]?: string[]
  [Filter.DeliverySites]?: string[]
  [Filter.AddedBy]?: string[]
  [Filter.Errors]?: string[]
  [Filter.Forwarded]?: string[]
  [Filter.Mac]?: string[]
  [Filter.HiddenByAdmin]?: string[]
  [Filter.HiddenByAuditor]?: string[]
  [Filter.ClientTypes]?: string[]
}
