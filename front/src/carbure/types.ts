import {
  EntityTypeEnum as EntityType,
  SiteTypeEnum as SiteType,
  GesOptionEnum as GESOption,
  PreferredUnitEnum as Unit,
  UserRightsRequestsStatusEnum as UserRightStatus,
  RoleEnum as UserRole,
  ExtAdminPagesEnum as ExternalAdminPages,
  TypeEnum as NotificationType,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export type Entity = apiTypes["UserEntity"]

export type EntityPreview = apiTypes["EntityPreview"]

export type User = apiTypes["UserSettingsResponseSeriaizer"]

export type UserRight = apiTypes["UserRights"]

export type UserRightRequest = apiTypes["UserRightsRequests"]

export type Notification = apiTypes["CarbureNotification"]

export type Feedstock = apiTypes["FeedStock"]

export type Biofuel = apiTypes["Biofuel"]

export type Country = apiTypes["Country"]

export type ProductionSite = apiTypes["ProductionSite"]

export type ProductionSiteDetails = ProductionSite & {
  inputs: Feedstock[]
  outputs: Biofuel[]
  certificates: Certificate[]
}

export type Depot = apiTypes["Depot"]

export type EntityDepot = apiTypes["EntitySite"]

export type Certificate = apiTypes["GenericCertificate"]

export interface EntityCertificate {
  id: number
  certificate: Certificate
  entity: Entity
  has_been_updated: boolean
  checked_by_admin: boolean
  rejected_by_admin: boolean
}

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

export enum OwnershipType {
  Own = "OWN",
  ThirdParty = "THIRD_PARTY",
  Processing = "PROCESSING",
}

export type CertificateType = apiTypes["CertificateTypeEnum"]

// Rename EntityTypeEnum generated by openapi-typescript to avoid changing EntityType to EntityTypeEnum
export { EntityType }

export { SiteType }

export { GESOption, Unit }

export { UserRightStatus }

export { UserRole }

export { ExternalAdminPages }

export { NotificationType }
