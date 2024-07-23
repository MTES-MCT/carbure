import { Entity } from "carbure/types"

export interface EntityDetails {
	entity: Entity
	users: number
	requests: number
	depots: number
	production_sites: number
	certificates: number
	certificates_pending: number
	double_counting: number
	double_counting_requests: number
	charge_points_accepted: number
	charge_points_pending: number
	meter_readings_pending: number
}
