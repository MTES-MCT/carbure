import { SummaryItem } from "transactions/types"

export type AdminStatus =
  | "alerts"
  | "corrections"
  | "declarations"
  | "stocks"
  | "pinned"
  | "unknown"

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
  lots: SummaryItem[]
}
