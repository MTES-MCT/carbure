import { Biofuel, Feedstock } from "common/types"
import { apiTypes } from "common/services/api-fetch.types"
import { PathsApiSafTicketSourcesGetParametersQueryStatus as SafTicketSourceStatus } from "api-schema"

export { SafTicketSourceStatus }

export type SafTicketSource = apiTypes["SafTicketSource"]

export type SafTicketSourceDetails = apiTypes["SafTicketSourceDetails"]

export interface SafTicketSourcesResponse {
  saf_ticket_sources: SafTicketSource[]
  from: number
  returned: number
  total: number
  ids: number[]
}

export interface SafTicketSourceSummaryItem extends SafTicketSourcePreview {
  year: number
  delivery_period: number
  total_volume: number
  feedstock: Feedstock
  biofuel: Biofuel
}

export type SafTicketSourcePreview = apiTypes["SafTicketSourcePreview"]
