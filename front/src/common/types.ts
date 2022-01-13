import { ExternalAdminPages } from "carbure/types"

export enum GESOption {
  Default = "Default",
  Actual = "Actual",
  NUTS2 = "NUTS2",
}

export enum EntityType {
  Producer = "Producteur",
  Operator = "Opérateur",
  Trader = "Trader",
  Administration = "Administration",
  Auditor = "Auditor",
  ExternalAdmin = "Administration Externe",
}

export enum CertificateType {
  ISCC = "ISCC",
  REDCERT = "REDCERT",
  SYSTEME_NATIONAL = "SYSTEME_NATIONAL",
  TWOBS = "2BS",
}

export interface Entity {
  id: number
  name: string
  entity_type: EntityType
  has_mac: boolean
  has_trading: boolean
  default_certificate: string
  ext_admin_pages?: ExternalAdminPages[]
}

export interface Country {
  code_pays: string
  name: string
  name_en: string
  is_in_europe: boolean
}

export interface MatierePremiere {
  code: string
  name: string
  is_double_compte?: boolean
  category: string
}

export interface Biocarburant {
  code: string
  name: string
}

export enum DepotType {
  EFS = "EFS",
  EFPE = "EFPE",
  Other = "OTHER",
  BiofuelDepot = "BIOFUEL DEPOT",
  OilDepot = "OIL DEPOT",
}

export enum OwnershipType {
  Own = "OWN",
  ThirdParty = "THIRD_PARTY",
  Processing = "PROCESSING",
}

export interface DeliverySite {
  name: string
  city: string
  depot_id: string
  country: Country
  depot_type: DepotType
  postal_code: string
  address: string
}

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
  inputs: MatierePremiere[]
  outputs: Biocarburant[]
  site_id: string
  postal_code: string
  city: string
  manager_name: string
  manager_phone: string
  manager_email: string
  certificates: Certificate[]
}

export interface Distance {
  distance: number
  link: string
  error: string // PRODUCTION_SITE_NOT_IN_CARBURE, DELIVERY_SITE_NOT_IN_CARBURE, PRODUCTION_SITE_COORDINATES_NOT_IN_CARBURE, DELIVERY_SITE_COORDINATES_NOT_IN_CARBURE, API_ERROR
  source: null | "DB" | "API"
}

export interface Lot {
  id: number
  carbure_id: string
  volume: number
  remaining_volume: number
  period: string
  source: string
  status: "Draft" | "Validated"
  data_origin_entity: Entity | null
  added_by: Entity | null
  added_time: string
  eccr: number
  eccs: number
  eec: number
  eee: number
  el: number
  ep: number
  esca: number
  etd: number
  eu: number
  ghg_reduction: number
  ghg_reference: number
  ghg_reference_red_ii: number
  ghg_reduction_red_ii: number
  ghg_total: number
  is_fused: boolean
  is_split: boolean
  biocarburant: Biocarburant
  matiere_premiere: MatierePremiere
  pays_origine: Country

  unknown_supplier: string | null
  unknown_supplier_certificate: string

  producer_is_in_carbure: boolean
  carbure_producer: Entity | null
  unknown_producer: string

  production_site_is_in_carbure: boolean
  carbure_production_site: ProductionSiteDetails | null
  carbure_production_site_reference: string
  unknown_production_site: string
  unknown_production_country: Country | null
  unknown_production_site_com_date: string | null
  unknown_production_site_dbl_counting: string | null
  unknown_production_site_reference: string

  parent_lot: Lot | null
  fused_with: null // @TODO
}

export enum DeliveryStatus {
  Pending = "N",
  ToFix = "AC",
  Fixed = "AA",
  Accepted = "A",
  Rejected = "R",
  Frozen = "F",
}

export interface Settings {
  email: string
  rights: UserRight[]
  requests: UserRightRequest[]
}

export interface EntityRights {
  rights: UserRight[]
  requests: UserRightRequest[]
}

export enum UserRole {
  ReadOnly = "RO",
  ReadWrite = "RW",
  Admin = "ADMIN",
  Auditor = "AUDITOR",
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

export type ProductionCertificate = {
  certificate_id: string
  holder: string
  type: "2BS" | "ISCC" | "REDCERT" | "SN"
}

export interface Declaration {
  id: number
  entity: Entity
  year: number
  month: number
  declared: false
  checked: false
  reminder_count: number
  lots: {
    drafts: number
    output: number
    input: number
    corrections: number
  }
}

export interface Depot {
  name: string
  city: string
  depot_id: string
  country: Country
  depot_type: DepotType
  postal_code: string
  address: string
}

export interface Feedstock {
  code: string
  name: string
  is_double_compte?: boolean
  category: string
}

export interface Biofuel {
  code: string
  name: string
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
  certificate: Certificate
  entity: Entity
  has_been_updated: boolean
}
