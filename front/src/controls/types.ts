import {
  Biofuel,
  Country,
  Declaration,
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
  vendor_certificate: string | null
  vendor_certificate_type: string | null
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
  parent_lot: number
  parent_stock: number
}

export interface LotList {
  lots: Lot[]
  from: number
  returned: number
  total: number
  total_errors: number
  total_deadline: number
  errors: Record<number, LotError[]>
  ids: number[]
}

export interface Stock {
  id: number
  carbure_id: string
  feedstock: Feedstock | null
  biofuel: Biofuel | null
  country_of_origin: Country | null
  initial_volume: number
  remaining_volume: number
  remaining_weight: number
  remaining_lhv_amount: number
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  production_country: Country | null
  carbure_supplier: Entity | null
  unknown_supplier: string | null
  carbure_client: Entity | null
  depot: Depot | null
  delivery_date: string | null
  period: number
  ghg_reduction: number
  ghg_reduction_red_ii: number
  parent_lot: number
  parent_transformation: number
}

export interface StockList {
  stocks: Stock[]
  total: number
  returned: number
  from: number
  ids: number[]
}

export interface Snapshot {
  lots: {
    alerts: number
    corrections: number
    declarations: number
    pinned: number
  }
}

export interface DeclarationSummary {
  period: number
  pending: number
  lots: number
  declaration: Declaration | null
}

export interface LotSummary {
  count: number
  total_volume: number
  lots: SummaryItem[]
}

export interface StockSummary {
  count: number
  total_remaining_volume: number
  total_volume?: number
  stock?: SummaryItem[]
}

export interface SummaryItem {
  client: string
  supplier: string
  biofuel_code: string
  volume_sum: number
  avg_ghg_reduction: number
  total: number
  pending: number
  remaining_volume_sum: number
}

export interface LotError {
  error: string
  is_blocking: boolean
  field: string
  fields: string[]
  value: string
  extra: string
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
  Depots = "depots",
  AddedBy = "added_by",
  Errors = "errors",
  Forwarded = "is_forwarded",
  Mac = "is_mac",
  HiddenByAdmin = "is_hidden_by_admin",
  HiddenByAuditor = "is_hidden_by_auditor",
  ClientTypes = "client_types",
  ShowEmpty = "show_empty",
}

export type FilterSelection = Partial<Record<Filter, string[]>>

export type Status =
  | "alerts"
  | "corrections"
  | "declarations"
  | "pinned"
  | "unknown"

export interface LotQuery {
  entity_id: number
  status?: string
  year?: number
  query?: string
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

export interface StockQuery {
  entity_id: number
  year?: number
  query?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  history?: boolean
  sort_by?: string
  order?: string
  selection?: number[]
  [Filter.Feedstocks]?: string[]
  [Filter.Biofuels]?: string[]
  [Filter.Periods]?: string[]
  [Filter.CountriesOfOrigin]?: string[]
  [Filter.Suppliers]?: string[]
  [Filter.ProductionSites]?: string[]
  [Filter.DeliverySites]?: string[]
}

export interface StockPayload {
  stock_id: number | undefined
  volume: number | undefined
  transport_document_type: string | undefined
  transport_document_reference: string | undefined
  delivery_date: string | undefined
  carbure_delivery_site_id: string | undefined
  unknown_delivery_site: string | undefined
  delivery_site_country_id: string | undefined
  delivery_type: string | undefined
  carbure_client_id: number | undefined
  unknown_client: string | undefined
}

export interface TransformETBEPayload {
  stock_id: number
  transformation_type: "ETH_ETBE",
  volume_ethanol: number
  volume_etbe: number
  volume_denaturant: number
  volume_etbe_eligible: number
}