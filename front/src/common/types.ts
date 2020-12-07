import { Option } from "./system/select"

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
}

export interface Entity {
  id: number
  name: string
  entity_type: EntityType
  has_mac: boolean
  has_trading: boolean
  national_system_certificate: string
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
}

export enum OwnershipType {
  Own = "OWN",
  ThirdParty = "THIRD_PARTY",
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
  certificates: Certificate[]
}

export interface Lot {
  id: number
  carbure_id: string
  volume: number
  period: string
  source: string
  status: "Draft" | "Validated"
  data_origin_entity: Entity | null
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
  ghg_total: number
  is_fused: boolean
  is_split: boolean
  biocarburant: Biocarburant
  matiere_premiere: MatierePremiere
  pays_origine: Country

  producer_is_in_carbure: boolean
  carbure_producer: Entity | null
  unknown_producer: string

  production_site_is_in_carbure: boolean
  carbure_production_site: ProductionSite | null
  unknown_production_site: string
  unknown_production_country: Country | null
  unknown_production_site_com_date: string | null
  unknown_production_site_dbl_counting: string
  unknown_production_site_reference: string

  parent_lot: null // @TODO
  fused_with: null // @TODO
}

export interface Transaction {
  id: number
  lot: Lot
  dae: string
  delivery_status: "N" | "AC" | "AA" | "A" | "R"
  delivery_date: string | null
  champ_libre: string
  is_mac: boolean

  vendor_is_in_carbure: boolean
  carbure_vendor: Entity | null
  unknown_vendor: string

  client_is_in_carbure: boolean
  carbure_client: Entity | null
  unknown_client: string

  delivery_site_is_in_carbure: boolean
  carbure_delivery_site: DeliverySite | null
  unknown_delivery_site: string
  unknown_delivery_site_country: Country | null

  errors: {
    field: string
    value: string
    error: string
  }[]
}

export interface TransactionError {
  tx_id: number
  field: string
  value: string
  error: string
}

export interface LotError {
  lot_id: number
  field: string
  value: string
  error: string
}

export interface Errors {
  tx_errors?: TransactionError[]
  lots_errors?: LotError[]
  validation_errors?: ValidationError[]
}

export interface ValidationError {
  lot_id: number
  error: string
  details: string
  fields: string[]
  is_warning: boolean
  is_blocking: boolean
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
    [id: string]: Errors
  }
}

export interface Comment {
  entity: Entity
  topic: string
  comment: string
}

export interface LotDetails {
  transaction: Transaction
  comments: Comment[]
  deadline: string
  errors: Errors
}

export enum Filters {
  MatieresPremieres = "matieres_premieres",
  Biocarburants = "biocarburants",
  Periods = "periods",
  ProductionSites = "production_sites",
  CountriesOfOrigin = "countries_of_origin",
  Clients = "clients",
  DeliverySites = "delivery_sites",
  Vendors = "vendors",
}

export interface Snapshot {
  lots: {
    [key in LotStatus]: number
  }

  filters: {
    [key in Filters]?: Option[]
  }

  years: Option[]
}

export interface Settings {
  email: string
  rights: UserRight[]
  requests: UserRightRequest[]
}

export interface UserRight {
  entity: Entity
  rights: string
}

export interface UserRightRequest {
  entity: Entity
  status: string
  date: Date
}

export interface StockSnapshot {
  lots: {
    [key in LotStatus]: number
  }

  filters: {
    [key in Filters]: Option[]
  }
}

export type DBSCertificate = {
  certificate_id: string
  certificate_holder: string
  holder_address: string
  valid_from: string
  valid_until: string
  certification_type: string
  scope: string[]
  has_been_updated: boolean
}

export type ISCCCertificate = {
  certificate_id: string
  certificate_holder: string
  location: string
  valid_from: string
  valid_until: string
  issuing_cb: string
  scope: string[]
  has_been_updated: boolean
}

export type Certificate = {
  certificate_id: string
  holder: string
  type: "2BS" | "ISCC"
}
