import { Entity } from "carbure/types"
import { Lot, LotError, Stock } from "transactions/types"

export interface LotDetails {
  lot: Lot
  parent_lot: Lot | null
  parent_stock: Stock | null
  children_lot: Lot[]
  children_stock: Stock[]
  distance: Distance | null
  updates: LotUpdate<any>[]
  comments: LotComment[]
  control_comments?: LotComment[]
  errors: LotError[]
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
  metadata: T
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
