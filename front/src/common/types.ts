import {
  EntityTypeEnum,
  SiteTypeEnum as SiteType,
  GesOptionEnum as GESOption,
  PreferredUnitEnum as Unit,
  UserRightsRequestsStatusEnum as UserRightStatus,
  RoleEnum as UserRole,
  ExtAdminPagesEnum as ExternalAdminPages,
  OwnershipTypeEnum as OwnershipType,
  PathsApiTiruertOperationsGetParametersQueryCustoms_category as CategoryEnum,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export type Entity = apiTypes["UserEntity"]

export type EntityPreview = apiTypes["EntityPreview"]

export type User = apiTypes["UserSettingsResponse"]

export type UserRight = apiTypes["UserRightsSettings"]

export type UserRightRequest = apiTypes["UserRightsRequests"]

export type Feedstock = apiTypes["FeedStock"]

export type FeedStockClassification = apiTypes["FeedStockClassification"]

export type Biofuel = apiTypes["Biofuel"]

export type Country = apiTypes["Country"]

export type ProductionSite = apiTypes["ProductionSite"]

export type ProductionSiteDetails = apiTypes["EntityProductionSite"]

export type Depot = apiTypes["Depot"]

export type EntityDepot = apiTypes["EntitySite"]

export type Airport = apiTypes["Airport"]

export type Certificate = apiTypes["GenericCertificate"]

export type EntityCertificate = apiTypes["EntityCertificate"]

export interface UploadCheckError {
  line: number
  error: string
  meta?: null | any
}

export interface UploadCheckReportInfo {
  errors?: UploadCheckError[]
  file_name: string
  error_count: number
}

// export type ExternalAdminPages = `${apiTypes["ExtAdminPagesEnum"]}`

export type CertificateType = apiTypes["CertificateTypeEnum"]

export { EntityTypeEnum as EntityType }

export { SiteType }

export { GESOption }

export { UserRightStatus }

export { UserRole }

export { ExternalAdminPages }

export { OwnershipType }

export { CategoryEnum }

// Add units that are used in specific modules
export enum ExtendedUnit {
  GJ = "gj",
  MWh = "MWh",
  tCO2ev = "tCO2ev",
}
export type ExtendedUnitType = Unit | ExtendedUnit

export { Unit }
/**
 * Make a type partial recursively
 */
export type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T

/**
 * Replace null with undefined recursively
 */
export type ReplaceNullWithUndefined<T> = {
  [K in keyof T]: T[K] extends null | undefined
    ? undefined
    : T[K] extends infer U | null
      ? U
      : T[K]
}
