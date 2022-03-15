export interface Entity {
  id: number
  name: string
  entity_type: EntityType
  has_mac: boolean
  has_trading: boolean
  has_stocks: boolean
  has_direct_deliveries: boolean
  default_certificate?: string
  ext_admin_pages?: ExternalAdminPages[]
}

export enum EntityType {
  Producer = "Producteur",
  Operator = "Opérateur",
  Trader = "Trader",
  Administration = "Administration",
  Auditor = "Auditor",
  ExternalAdmin = "Administration Externe",
  Unknown = "Unknown",
}

export type ExternalAdminPages = "DCA" | "TIRIB"

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

export enum UserRightStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
  Revoked = "REVOKED",
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

export enum UserRole {
  ReadOnly = "RO",
  ReadWrite = "RW",
  Admin = "ADMIN",
  Auditor = "AUDITOR",
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

export enum NotificationType {
  CorrectionRequest = "CORRECTION_REQUEST",
  CorrectionDone = "CORRECTION_DONE",
  LotsRejected = "LOTS_REJECTED",
  LotsReceived = "LOTS_RECEIVED",
  LotsRecalled = "LOTS_RECALLED",
  CertificateExpired = "CERTIFICATE_EXPIRED",
  // DeclarationValidated = "DECLARATION_VALIDATED",
  // DeclarationCancelled = "DECLARATION_CANCELLED"
}
