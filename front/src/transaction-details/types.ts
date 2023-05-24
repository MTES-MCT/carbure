import { Entity } from "carbure/types"
import { Lot, LotError, Stock } from "transactions/types"

export interface LotDetails {
  lot: Lot
  parent_lot: Lot | null
  parent_stock: Stock | null
  has_parent_stock: boolean | null
  children_lot: Lot[]
  children_stock: Stock[]
  distance: Distance | null
  updates: LotUpdate<any>[]
  comments: LotComment[]
  control_comments?: LotComment[]
  errors: LotError[]
  certificates: LotCertificates
  score: LotScore[]
  disabled_fields: string[]
}

export interface Distance {
  distance?: number
  link?: string
  error?: string
  source?: string
}

export interface LotUpdate<T> {
  user: string
  event_type: string
  event_dt: string
  metadata?: T
  label?: string
}

export interface LotFieldUpdate {
  added: any[]
  removed: []
  changed: [string, any, any][] // [field, value_before, value_after]
}

export interface LotComment {
  entity: Entity
  user: string
  comment_type: string
  comment_dt: string
  comment: string
}

export interface LotCertificates {
  production_site_certificate: LotCertificate | null
  supplier_certificate: LotCertificate | null
  vendor_certificate: LotCertificate | null
  production_site_double_counting_certificate: LotCertificate | null
}

export interface LotCertificate {
  holder: string
  valid_until: string
  valid_from: string
  matches: number
  found: boolean
  certificate_id: string
  certificate_type: string
}

export interface LotScore {
  item: string
  max_score: number
  score: number
  meta: Record<string, boolean> | null
}

export interface StockDetails {
  stock: Stock
  parent_lot: Lot | null
  parent_transformation: StockTransformation | null
  children_lot: Lot[]
  children_transformation: StockTransformation[]
  updates: LotUpdate<any>[]
  comments: LotComment[]
}

export interface StockTransformation<T = any> {
  transformation_type: "ETH_ETBE" | string
  source_stock: Stock
  dest_stock: Stock
  volume_deducted_from_source: number
  volume_destination: number
  metadata: T
  transformed_by: number
  entity: number
  transformation_dt: string
}

export interface ETBETransformation {
  volume_denaturant: number
  volume_etbe_eligible: number
}
