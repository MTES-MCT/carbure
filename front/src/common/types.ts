import { Entity } from "carbure/types"

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

export interface Country {
  code_pays: string
  name: string
  name_en: string
  is_in_europe: boolean
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
  inputs: Feedstock[]
  outputs: Biofuel[]
  site_id: string
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
