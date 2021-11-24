import { Entity } from "carbure/types"
import { Lot, LotError } from "transactions-v2/types"

export interface LotDetails {
  lot: Lot
  children: Lot[]
  distance: Distance
  updates: LotUpdate<any>[]
  comments: LotComment[]
  errors: LotError[]
}

export interface Distance {
  distance?: number
  link?: string
  error?: string
  source?: string
}

export interface LotUpdate<T = LotFieldUpdate> {
  user: string
  event_type: string
  event_dt: string
  metadata: T
  label?: string
}

export interface LotFieldUpdate {
  field: string
  value_before: string | number | null
  value_after: string | number | null
}

export interface LotComment {
  entity: Entity
  user: string
  comment_type: string
  comment_dt: string
  comment: string
}
