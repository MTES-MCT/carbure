import { LotComment, LotUpdate } from "lot-details/types"
import { Stock } from "transactions-v2/types"

export interface StockDetails {
  stock: Stock
  children: Stock[]
  updates: LotUpdate<any>[]
  comments: LotComment[]
}
