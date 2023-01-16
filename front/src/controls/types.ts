import { SummaryItem } from "transactions/types"

export type AdminStatus = "alerts" | "lots" | "stocks" | "unknown"

export interface Snapshot {
  lots: {
    alerts: number
    lots: number
    stocks: number
    pinned: number
  }
}

export interface LotSummary {
  count: number
  total_volume: number
  total_weight: number
  total_lhv_amount: number
  lots: SummaryItem[]
}


export interface LotUpdateManyQuery {
  lots_ids: number[],
  values: string[]
  entities_to_notify: string[]
}