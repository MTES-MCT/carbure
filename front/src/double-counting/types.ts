import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  ProductionSite,
} from "carbure/types"

export enum Admin {
  DGEC = "MTE - DGEC",
  DGDDI = "DGDDI",
  DGPE = "DGPE",
}

export enum DoubleCountingStatus {
  Pending = "PENDING",
  InProgress = "INPROGRESS",
  Rejected = "REJECTED",
  Accepted = "ACCEPTED",
  Lapsed = "LAPSED",
}

export interface DoubleCountingApplication {
  id: number
  agreement_id: string
  producer: Entity
  production_site: string
  period_start: string
  period_end: string
  status: DoubleCountingStatus
  producer_user: string
  created_at: string
}

export interface DoubleCountingSourcingAggregation {
  year: number
  sum: number
  count: number
  feedstock: Feedstock
}

export interface DoubleCountingSourcing {
  id: number
  year: number
  metric_tonnes: number
  feedstock: Feedstock
  origin_country: Country
  transit_country?: Country
  supply_country?: Country
}

export interface DoubleCountingProduction {
  id: number
  year: number
  feedstock: Feedstock
  biofuel: Biofuel
  max_production_capacity?: number
  estimated_production: number
  requested_quota: number
  approved_quota: number
}

export enum DoubleCountingUploadErrorType {
  UnkownBiofuel = "UNKNOWN_BIOFUEL",
  MissingBiofuel = "MISSING_BIOFUEL",
  NotDcFeedstock = "NOT_DC_FEEDSTOCK",
  MpBcIncoherent = "MP_BC_INCOHERENT",
  ProductionMismatchSourcing = "PRODUCTION_MISMATCH_SOURCING",
  PomeGt2000 = "POME_GT_2000",
  MissingEstimatedProduction = "MISSING_ESTIMATED_PRODUCTION",
  MissingMaxProductionCapacity = "MISSING_MAX_PRODUCTION_CAPACITY",
  MissingFeedstock = "MISSING_FEEDSTOCK",
  MissingData = "MISSING_DATA",
  ProductionMismatchQuota = "PRODUCTION_MISMATCH_QUOTA",
  UnknownYear = "UNKNOWN_YEAR",
  InvalidYear = "INVALID_YEAR",
  BadWorksheetName = "BAD_WORKSHEET_NAME",
  MissingCountryOfOrigin = "MISSING_COUNTRY_OF_ORIGIN",
}

export interface DoubleCountingUploadError {
  error: string
  is_blocking: boolean
  line_number: number | null
  line_merged?: string
  meta?: null | any
}

export interface DoubleCountingUploadErrors extends DoubleCountingApplication {
  // sourcing_history?: DoubleCountingUploadError[]
  sourcing_forecast?: DoubleCountingUploadError[]
  production?: DoubleCountingUploadError[]
  global?: DoubleCountingUploadError[]
}

export interface DoubleCountingDetails extends DoubleCountingApplication {
  sourcing: DoubleCountingSourcing[]
  production: DoubleCountingProduction[]
  aggregated_sourcing: DoubleCountingSourcingAggregation[]
  documents: { id: number; url: string; file_type: "DECISION" | "SOURCING" }[]
  dgec_validated: boolean
  dgec_validator: string | null
  dgec_validated_dt: string | null
  dgddi_validated: boolean
  dgddi_validator: string | null
  dgddi_validated_dt: string | null
  dgpe_validated: boolean
  dgpe_validator: string | null
  dgpe_validated_dt: string | null
}
export interface ApplicationSnapshot {
  applications_pending: number
  applications_rejected: number
}

export interface AgreementsSnapshot {
  agreements_active: number
  agreements_expired: number
  agreements_incoming: number
}

export interface DoubleCountingSnapshot extends AgreementsSnapshot, ApplicationSnapshot { }

export interface ApplicationsOverview {
  rejected: { count: number; applications: DoubleCountingApplication[] }
  pending: { count: number; applications: DoubleCountingApplication[] }
}

export interface QuotaOverview {
  producer: Entity
  production_site: ProductionSite
  approved_quota_weight_sum: number
  current_production_weight_sum: number
  nb_quotas: number
  nb_full_quotas: number
  nb_breached_quotas: number
}

export interface QuotaDetails {
  volume: number
  approved_quota: number
  current_production_weight_sum_tonnes: number
  feedstock: Feedstock
  biofuel: Biofuel
  nb_lots: number
}

export interface DoubleCountingFileInfo {
  has_dechets_industriels: boolean
  errors?: DoubleCountingUploadErrors
  start_year: string
  file_name: string
  producer_email: string
  production_site: string
  error_count: number
  production: DoubleCountingProduction[]
  sourcing: DoubleCountingSourcing[]
}

export interface CheckDoubleCountingFilesResponse {
  files: DoubleCountingFileInfo[]
  checked_at: string
}
