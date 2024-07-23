import { LotError, SummaryItem } from "transactions/types"

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

export interface LotsUpdateErrors {
	[key: number]: LotError[]
}

export interface UpdateInfo {
	node: any
	diff: Record<string, [any, any]>
}

export interface LotsUpdateResponse {
	errors?: LotsUpdateErrors
	updates?: UpdateInfo[]
}

export interface LotsDeleteResponse {
	deletions?: UpdateInfo[]
	updates?: UpdateInfo[]
}
