import { apiTypes } from "common/services/api-fetch.types"

export interface Entity {
  id: number
  name: string
  entity_type: EntityType
  legal_name: string
  registration_id: string
  sustainability_officer_phone_number: string
  sustainability_officer_email?: string
  sustainability_officer: string
  registered_address: string
  registered_city: string
  registered_zipcode: string
  registered_country?: Country
  has_mac: boolean
  has_trading: boolean
  has_stocks: boolean
  has_direct_deliveries: boolean
  preferred_unit?: Unit
  default_certificate?: string
  ext_admin_pages?: ExternalAdminPages[]
  has_saf?: boolean
  has_elec: boolean
  activity_description?: string
  website?: string
  vat_number?: string
}

export interface EntityPreview {
  id: number
  name: string
  entity_type: EntityType
}

export interface User {
  email: string
  rights: UserRight[]
  requests: UserRightRequest[]
}

export interface UserRight {
  entity: Entity
  date_added: string
  expiration_date: string
  role: UserRole
}

export interface UserRightRequest {
  id: number
  user: [string]
  entity: Entity
  status: UserRightStatus
  date_requested: string
  expiration_date: string
  comment: string
  role: UserRole
}

export interface Notification {
  id: number
  dest: Entity
  datetime: string
  type: NotificationType
  acked: boolean
  send_by_email: boolean
  email_sent: boolean
  meta: null | any
}

export type Feedstock = apiTypes["FeedStock"]

export interface Biofuel {
  code: string
  name: string
}

export type Country = apiTypes["Country"]

export interface ProductionSite {
  id: number
  name: string
  country: Country
  date_mise_en_service: string
  dc_reference: string | undefined
}

export interface ProductionSiteDetails extends ProductionSite {
  date_mise_en_service: string
  ges_option: GESOption
  eligible_dc: boolean
  dc_reference: string | undefined
  inputs: Feedstock[]
  outputs: Biofuel[]
  site_id: string
  address: string
  postal_code: string
  city: string
  manager_name: string
  manager_phone: string
  manager_email: string
  certificates: Certificate[]
}

export interface Depot {
  name: string
  city: string
  depot_id: string
  country: Country
  depot_type: DepotType
  postal_code: string
  address: string
  electrical_efficiency: number | null
  thermal_efficiency: number | null
  useful_temperature: number | null
}

export interface EntityDepot {
  depot: Depot | null
  ownership_type: OwnershipType
  blending_is_outsourced: boolean
  blender: Entity | null
}

export interface Certificate {
  certificate_id: string
  certificate_type: CertificateType
  certificate_holder: string
  certificate_issuer: string
  address: string
  valid_from: string
  valid_until: string
  download_link: string
  scope: string
  input: string
  output: string
}

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

export type Unit = "l" | "kg" | "MJ"

export type ExternalAdminPages = "DCA" | "TIRIB" | "AIRLINE" | "ELEC"

export enum EntityType {
  Producer = "Producteur",
  Operator = "Opérateur",
  Airline = "Compagnie aérienne",
  Trader = "Trader",
  Administration = "Administration",
  Auditor = "Auditor",
  ExternalAdmin = "Administration Externe",
  CPO = "Charge Point Operator",
  Unknown = "Unknown",
  PowerOrHeatProducer = "Power or Heat Producer",
}

export enum UserRole {
  ReadOnly = "RO",
  ReadWrite = "RW",
  Admin = "ADMIN",
  Auditor = "AUDITOR",
}

export enum UserRightStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
  Revoked = "REVOKED",
}

export enum NotificationType {
  CorrectionRequest = "CORRECTION_REQUEST",
  CorrectionDone = "CORRECTION_DONE",
  LotsRejected = "LOTS_REJECTED",
  LotsReceived = "LOTS_RECEIVED",
  LotsRecalled = "LOTS_RECALLED",
  CertificateExpired = "CERTIFICATE_EXPIRED",
  CertificateRejected = "CERTIFICATE_REJECTED",

  DeclarationValidated = "DECLARATION_VALIDATED",
  DeclarationCancelled = "DECLARATION_CANCELLED",
  DeclarationReminder = "DECLARATION_REMINDER",

  MeterReadingsApplicationStarted = "METER_READINGS_APP_STARTED",
  MeterReadingsApplicationEndingSoon = "METER_READINGS_APP_ENDING_SOON",

  SafTicketReceived = "SAF_TICKET_RECEIVED",
  SafTicketAccepted = "SAF_TICKET_ACCEPTED",
  SafTicketRejected = "SAF_TICKET_REJECTED",

  LotsUpdatedByAdmin = "LOTS_UPDATED_BY_ADMIN",
  LotsDeletedByAdmin = "LOTS_DELETED_BY_ADMIN",
}

export enum DepotType {
  EFS = "EFS",
  EFPE = "EFPE",
  EFCA = "EFCA",
  Other = "OTHER",
  BiofuelDepot = "BIOFUEL DEPOT",
  OilDepot = "OIL DEPOT",
  PowerPlant = "POWER PLANT",
  HeatPlant = "HEAT PLANT",
  CogenerationPlant = "COGENERATION PLANT",
}

export enum OwnershipType {
  Own = "OWN",
  ThirdParty = "THIRD_PARTY",
  Processing = "PROCESSING",
}

export enum CertificateType {
  ISCC = "ISCC",
  REDCERT = "REDCERT",
  SYSTEME_NATIONAL = "SYSTEME_NATIONAL",
  TWOBS = "2BS",
}

export enum GESOption {
  Default = "Default",
  Actual = "Actual",
  NUTS2 = "NUTS2",
}
