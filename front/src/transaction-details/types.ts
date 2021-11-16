import { Entity } from "carbure/types"
import { Lot } from "transactions-v2/types"

export interface LotDetails {
  lot: Lot
  children: Lot[]
  distance: Distance
  deadline: string
  errors: LotError[]
  updates: LotUpdate<any>[]
  comments: LotComment[]
}

export interface Distance {
  distance?: number
  link?: string
  error?: string
  source?: string
}

export interface LotError {
  error: string
  is_blocking: boolean
  field: string
  fields: string[]
  value: string
  extra: string
}

export interface LotUpdate<T = any> {
  user: string
  event_type: string
  event_dt: string
  metadata: T
}

export interface LotComment {
  entity: Entity
  user: string
  comment_type: string
  comment_dt: string
  comment: string
}
