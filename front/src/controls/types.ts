import { SummaryItem } from "transactions/types"

export type AdminStatus =
  | "alerts"
  | "corrections"
  | "declarations"
  | "pinned"
  | "unknown"

export interface Snapshot {
  lots: {
    alerts: number
    corrections: number
    declarations: number
    pinned: number
  }
}

export interface LotSummary {
  count: number
  total_volume: number
  lots: SummaryItem[]
}
