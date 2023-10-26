import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  ProductionSite,
  ProductionSiteDetails,
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

export enum AgreementStatus {
  Active = "ACTIVE",
  Expired = "EXPIRED",
  ExpiresSoon = "EXPIRES_SOON",
  Incoming = "INCOMING",
}

export interface DoubleCountingApplicationOverview {
  id: number
  agreement_id: string
  producer: Entity
  production_site: ProductionSiteDetails
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


export interface DoubleCountingQuota {
  approved_quota: number
  biofuel: Biofuel
  feedstock: Feedstock
  id: number
  lot_count: number
  production_tonnes: number
  quotas_progression: number
  requested_quota: number
  year: number
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

export interface DoubleCountingUploadErrors extends DoubleCountingApplicationOverview {
  // sourcing_history?: DoubleCountingUploadError[]
  sourcing_forecast?: DoubleCountingUploadError[]
  production?: DoubleCountingUploadError[]
  global?: DoubleCountingUploadError[]
}

export interface DoubleCountingApplicationDetails extends DoubleCountingApplicationOverview {
  sourcing: DoubleCountingSourcing[]
  production: DoubleCountingProduction[]
  aggregated_sourcing: DoubleCountingSourcingAggregation[]
  documents: { id: number; url: string; file_type: "DECISION" | "SOURCING" }[]
}
export interface DoubleCountingApplicationSnapshot {
  applications_pending: number
  applications_rejected: number
}

export interface DoubleCountingAgreementsSnapshot {
  agreements_active: number
  agreements_expired: number
  agreements_incoming: number
}

export interface DoubleCountingSnapshot extends DoubleCountingAgreementsSnapshot, DoubleCountingApplicationSnapshot { }

export interface DoubleCountingApplicationsOverview {
  rejected: DoubleCountingApplicationOverview[]
  pending: DoubleCountingApplicationOverview[]
}

export interface DoubleCountingAgreementsOverview {
  active: DoubleCountingAgreementOverview[]
  incoming: DoubleCountingAgreementOverview[]
  expired: DoubleCountingAgreementOverview[]
}
export interface DoubleCountingAgreementOverview {
  id: number
  producer: Entity
  production_site: ProductionSite
  certificate_id: string
  valid_from: Date
  valid_until: Date
  status: AgreementStatus
}

export interface AgreementDetails extends DoubleCountingAgreementOverview {
  application: DoubleCountingApplicationDetails
  quotas: DoubleCountingQuota[]
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
