import { LotComment, LotUpdate } from "lot-details/types"
import { Lot, Stock } from "transactions/types"

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
