import { LotComment, LotUpdate } from "lot-details/types"
import { Lot, Stock } from "transactions-v2/types"

export interface StockDetails {
  stock: Stock
  parent_lot: Lot | null
  parent_transformation: Lot | null
  children_lot: Lot[]
  children_transformation: Lot[]
  updates: LotUpdate<any>[]
  comments: LotComment[]
}
