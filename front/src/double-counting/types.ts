import { DoubleCountingStatus, DoubleCountingAgreementStatus } from "api-schema"
import {
  Biofuel,
  Entity,
  Feedstock,
  ProductionSiteDetails,
} from "carbure/types"
import { apiTypes } from "common/services/api-fetch.types"

export { DoubleCountingStatus }
export { DoubleCountingAgreementStatus as AgreementStatus }

export enum Admin {
  DGEC = "MTE - DGEC",
  DGDDI = "DGDDI",
  DGPE = "DGPE",
}

export enum DoubleCountingExtendedStatus {
  ACCEPTED = DoubleCountingStatus.ACCEPTED,
  INPROGRESS = DoubleCountingStatus.INPROGRESS,
  PENDING = DoubleCountingStatus.PENDING,
  REJECTED = DoubleCountingStatus.REJECTED,
  EXPIRED = DoubleCountingAgreementStatus.EXPIRED,
  EXPIRES_SOON = DoubleCountingAgreementStatus.EXPIRES_SOON,
  INCOMING = DoubleCountingAgreementStatus.INCOMING,
}

export type DoubleCountingApplicationOverview =
  apiTypes["DoubleCountingApplicationPartial"]

export interface DoubleCountingSourcingAggregation {
  year: number
  sum: number
  count: number
  feedstock: Feedstock
}

export type DoubleCountingSourcing = apiTypes["DoubleCountingSourcing"]

export type DoubleCountingProduction = apiTypes["DoubleCountingProduction"]

export type DoubleCountingQuota = apiTypes["DoubleCountingQuota"]

export enum DoubleCountingUploadErrorType {
  UnkownBiofuel = "UNKNOWN_BIOFUEL",
  MissingBiofuel = "MISSING_BIOFUEL",
  FeedstockNotDoubleCounting = "FEEDSTOCK_NOT_DOUBLE_COUNTING",
  MpBcIncoherent = "MP_BC_INCOHERENT",
  ProductionMismatchSourcing = "PRODUCTION_MISMATCH_SOURCING",
  PomeGt2000 = "POME_GT_2000",
  MissingEstimatedProduction = "MISSING_ESTIMATED_PRODUCTION",
  MissingMaxProductionCapacity = "MISSING_MAX_PRODUCTION_CAPACITY",
  MissingFeedstock = "MISSING_FEEDSTOCK",
  MissingData = "MISSING_DATA",
  ProductionMismatchQuota = "PRODUCTION_MISMATCH_QUOTA",
  ProductionMismatchProductionMax = "PRODUCTION_MISMATCH_PRODUCTION_MAX",
  UnknownYear = "UNKNOWN_YEAR",
  InvalidYear = "INVALID_YEAR",
  BadWorksheetName = "BAD_WORKSHEET_NAME",
  MissingCountryOfOrigin = "MISSING_COUNTRY_OF_ORIGIN",
  UnknownCountryOfOrigin = "UNKNOWN_COUNTRY_OF_ORIGIN",
}

export type DoubleCountingUploadErrors = apiTypes["FileErrors"]

export type DoubleCountingUploadError = apiTypes["FileError"] & {
  meta?: any | null
}

export type DoubleCountingApplicationDetails =
  apiTypes["DoubleCountingApplication"]

export interface DoubleCountingApplicationSnapshot {
  applications_pending: number
  applications_rejected: number
}

export interface DoubleCountingAgreementsSnapshot {
  agreements_active: number
  agreements_expired: number
  agreements_incoming: number
}

export type DoubleCountingSnapshot = apiTypes["ApplicationSnapshot"]

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
  production_site: ProductionSiteDetails
  certificate_id: string
  valid_from: Date
  valid_until: Date
  status: DoubleCountingAgreementStatus
  quotas_progression: number
}

export type DoubleCountingAgreementPublic =
  apiTypes["DoubleCountingRegistrationPublic"]

export type AgreementDetails = apiTypes["DoubleCountingRegistrationDetails"]

export interface QuotaDetails {
  volume: number
  approved_quota: number
  current_production_weight_sum_tonnes: number
  feedstock: Feedstock
  biofuel: Biofuel
  nb_lots: number
}

export type DoubleCountingFileInfo = apiTypes["CheckFileResponse"]["file"]

export interface CheckDoubleCountingFilesResponse {
  files: DoubleCountingFileInfo[]
  checked_at: string
}
