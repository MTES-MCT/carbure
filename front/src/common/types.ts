import { Option } from "./components/select"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"

export type Pagination = {
  from?: number
  limit?: number
}

export enum LotStatus {
  Draft = "draft",
  Validated = "validated",
  ToFix = "tofix",
  Accepted = "accepted",
  Weird = "weird",
  Stock = "stock",
  Inbox = "in",
  ToSend = "tosend",
  Alert = "alert",
  Correction = "correction",
  Declaration = "declaration",
  Highlight = "highlight",
}

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
  ExternalAdmin = "Administration Externe"
}

export enum ExternalAdminPages {
  DoubleCounting = 'DCA',
  Tirib = 'TIRIB'
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

export interface MatierePremiereDetails extends MatierePremiere {
  description: string
  compatible_alcool: boolean
  compatible_graisse: boolean
}

export interface Biocarburant {
  code: string
  name: string
}

export interface BiocarburantDetails extends Biocarburant {
  description: string
  pci_kg: number
  pci_litre: number
  masse_volumique: number
  is_alcool: boolean
  is_graisse: boolean
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
}

export interface ProductionSiteDetails extends ProductionSite {
  date_mise_en_service: string
  ges_option: GESOption
  eligible_dc: boolean
  dc_reference: string | null
  inputs: MatierePremiere[]
  outputs: Biocarburant[]
  site_id: string
  postal_code: string
  city: string
  manager_name: string
  manager_phone: string
  manager_email: string
  certificates: ProductionCertificate[]
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

export interface Transaction {
  id: number
  lot: Lot
  dae: string
  delivery_status: DeliveryStatus
  delivery_date: string | null
  champ_libre: string
  is_mac: boolean
  is_forwarded: boolean
  parent_tx: number | null

  carbure_vendor: Entity | null
  carbure_vendor_certificate: string

  client_is_in_carbure: boolean
  carbure_client: Entity | null
  unknown_client: string

  delivery_site_is_in_carbure: boolean
  carbure_delivery_site: DeliverySite | null
  unknown_delivery_site: string
  unknown_delivery_site_country: Country | null

  hidden_by_admin: boolean
  hidden_by_auditor: boolean
  highlighted_by_admin: boolean
  highlighted_by_auditor: boolean
}

export interface GenericError {
  error: string

  display_to_creator: boolean
  display_to_recipient: boolean
  display_to_admin: boolean
  display_to_auditor: boolean

  acked_by_creator: boolean
  acked_by_recipient: boolean
  acked_by_admin: boolean
  acked_by_auditor: boolean

  highlighted_by_admin: boolean
  highlighted_by_auditor: boolean

  is_blocking: boolean

  tx: number

  field: string | null
  fields: string[] | null
  value: string
  extra: string
}

export interface Lots {
  from: number
  returned: number
  total: number
  total_errors: number

  lots: Transaction[]

  deadlines: {
    date: string
    total: number
  }

  errors: {
    [id: string]: GenericError[]
  }
}

export interface Comment {
  entity?: Entity
  topic?: string
  comment: string
}

export interface LotUpdate {
  tx_id: number
  update_type: "ADD" | "UPDATE" | "REMOVE"
  datetime: string
  field: string
  label?: string
  value_before: string | null
  value_after: string | null
  modified_by: string
}

export interface LotDetails {
  transaction: Transaction
  comments: Comment[]
  admin_comments?: Comment[]
  deadline: string
  errors: GenericError[]
  updates?: LotUpdate[]
  distance?: Distance
  certificates: {
    production_site_certificate: CertificateInfo | null
    supplier_certificate: CertificateInfo | null
    vendor_certificate: CertificateInfo | null
    double_counting_reference: DoubleCountingCertificateInfo | null
    unknown_production_site_dbl_counting: DoubleCountingCertificateInfo | null
  }
}

export enum Filters {
  DeliveryStatus = "delivery_status",
  MatieresPremieres = "matieres_premieres",
  Biocarburants = "biocarburants",
  Periods = "periods",
  CountriesOfOrigin = "countries_of_origin",
  Vendors = "vendors",
  Clients = "clients",
  ProductionSites = "production_sites",
  DeliverySites = "delivery_sites",
  AddedBy = "added_by",
  Errors = "errors",
  Forwarded = "is_forwarded",
  Mac = "is_mac",
  HiddenByAdmin = "is_hidden_by_admin",
  HiddenByAuditor = "is_hidden_by_auditor",
  ClientTypes = "client_types",
  ShowEmpty = "show_empty",
}

export interface TransactionQuery {
  entity_id: number
  status: LotStatus
  from_idx?: number
  sort_by?: string
  year?: number
  limit?: number | null
  query?: string
  order?: string
  invalid?: boolean
  deadline?: boolean
  [Filters.DeliveryStatus]?: any
  [Filters.MatieresPremieres]?: any
  [Filters.Biocarburants]?: any
  [Filters.Periods]?: any
  [Filters.CountriesOfOrigin]?: any
  [Filters.Vendors]?: any
  [Filters.Clients]?: any
  [Filters.ProductionSites]?: any
  [Filters.DeliverySites]?: any
  [Filters.AddedBy]?: any
  [Filters.Errors]?: any
  [Filters.Forwarded]?: any
  [Filters.Mac]?: any
  [Filters.HiddenByAdmin]?: any
  [Filters.HiddenByAuditor]?: any
  [Filters.ClientTypes]?: any
  // [Filters.HighlightedByAdmin]?: any
  // [Filters.HighlightedByAuditor]?: any
}

export interface Snapshot {
  lots: {
    [key in LotStatus]?: number
  }

  filters: Filters[]
  years: Option[]
  depots: EntityDeliverySite[]
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

export type DBSCertificate = {
  type: string
  certificate_id: string
  certificate_holder: string
  holder_address: string
  valid_from: string
  valid_until: string
  certification_type: string
  scope: string[]
  has_been_updated: boolean
  download_link: string
}

export type ISCCCertificate = {
  type: string
  certificate_id: string
  certificate_holder: string
  location: string
  valid_from: string
  valid_until: string
  issuing_cb: string
  scope: string[]
  has_been_updated: boolean
  download_link: string
}

export type REDCertCertificate = {
  type: string
  certificate_id: string
  certificate_holder: string
  city: string
  zip_code: string
  country_raw: string
  valid_from: string
  valid_until: string
  certificator: string
  certificate_type: string
  status: string
  scope: string[]
  has_been_updated: boolean
  download_link: string
}

export type SNCertificate = {
  type: string
  certificate_id: string
  certificate_holder: string
  valid_from: string
  valid_until: string
  scope: string[]
  has_been_updated: boolean
  download_link: string
}

export type Certificate =
  | ISCCCertificate
  | DBSCertificate
  | REDCertCertificate
  | SNCertificate

export interface CertificateInfo {
  certificate_id: string
  certificate_type: "2BS" | "ISCC" | "REDCERT" | "SN"
  holder: string
  valid_from: string
  valid_until: string
  matches: number
  found: boolean
  scope: string[]
}

export interface DoubleCountingCertificateInfo {
  certificate_id: string
  holder: string
  valid_from: string
  valid_until: string
  matches: number
  found: boolean
}

export type ProductionCertificate = {
  certificate_id: string
  holder: string
  type: "2BS" | "ISCC" | "REDCERT" | "SN"
}

export type StockDraft = {
  tx_id: number
  volume: number
  dae: string
  delivery_date: string
  client: string
  delivery_site: string
  delivery_site_country?: string
  mac: boolean
  vendor_certificate: string
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

export interface SummaryItem {
  entity?: string
  vendor?: string
  client?: string
  depot: string
  biocarburant: string
  lots: number
  volume: number
  avg_ghg_reduction: number
}

export interface TransactionSummary {
  in?: SummaryItem[]
  out?: SummaryItem[]
  transactions?: SummaryItem[]
  tx_ids: number[]
  total_volume: number
  total_remaining_volume: number
}

export interface ConvertETBE {
  previous_stock_tx_id?: number
  volume_ethanol: number
  volume_etbe: number
  volume_etbe_eligible: number
  volume_denaturant: number
}

export enum DoubleCountingStatus {
  Pending = "PENDING",
  InProgress = "INPROGRESS",
  Rejected = "REJECTED",
  Accepted = "ACCEPTED",
  Lapsed = "LAPSED",
}

export interface DoubleCounting {
  id: number
  producer: Entity
  production_site: string
  period_start: string
  period_end: string
  status: DoubleCountingStatus
  producer_user: string
  creation_date: string
}

export interface DoubleCountingSourcingAggregation {
  year: number
  sum: number
  count: number
  feedstock: MatierePremiere
}

export interface DoubleCountingSourcing {
  id: number
  year: number
  metric_tonnes: number
  feedstock: MatierePremiere
  origin_country: Country
  transit_country?: Country
  supply_country?: Country
}

export interface DoubleCountingProduction {
  id: number
  year: number
  feedstock: MatierePremiere
  biofuel: Biocarburant
  max_production_capacity?: number
  estimated_production: number
  requested_quota: number
  approved_quota: number
}

export interface DoubleCountingDetails extends DoubleCounting {
  sourcing: DoubleCountingSourcing[]
  production: DoubleCountingProduction[]
  aggregated_sourcing: DoubleCountingSourcingAggregation[]
  documents: { id: number, url: string }[]
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

export enum Admin {
  DGEC = "MTE - DGEC",
  DGDDI = "DGDDI",
  DGPE = "DGPE",
}