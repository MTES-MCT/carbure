import { Option } from "../components/dropdown/select"

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
}

export type CarbureClient = any
export type CarbureDeliverySite = any
export type CarbureVendor = any

export type Country = {
  code_pays: string
  name: string
  name_en: string
  is_in_europe: boolean
}

export type LotDetails = {
  id: 1
  carbure_id: string
  volume: number
  parent_lot: null // @TODO
  period: string
  source: string
  status: LotStatus
  data_origin_entity: null // @TODO
  eccr: number
  eccs: number
  eec: number
  eee: number
  el: number
  ep: number
  esca: number
  etd: number
  eu: number
  fused_with: null // @TODO
  ghg_reduction: number
  ghg_reference: number
  ghg_total: number
  is_fused: boolean
  is_split: boolean

  pays_origine: Country

  biocarburant: {
    code: string
    name: string
  }
  carbure_producer: {
    id: number
    name: string
    entity_type: string
  }
  carbure_production_site: {
    id: number
    name: string
    country: Country
  }

  matiere_premiere: {
    code: string
    name: string
  }

  producer_is_in_carbure: boolean
  production_site_is_in_carbure: boolean
  unknown_producer: string | null
  unknown_production_country: string | null
  unknown_production_site: string | null
  unknown_production_site_com_date: string | null
  unknown_production_site_dbl_counting: string | null
  unknown_production_site_reference: string | null
}

export type Lot = {
  lot: LotDetails
  delivery_status: string
  dae: string
  delivery_date: string
  carbure_vendor: CarbureVendor
  carbure_client: CarbureClient
  carbure_delivery_site: CarbureDeliverySite
  unknown_client: string | null
  unknown_vendor: string | null
  unknown_delivery_site: string | null
  unknown_delivery_site_country: any | null
  champ_libre: string
  is_mac: boolean
  vendor_is_in_carbure: boolean
  delivery_site_is_in_carbure: boolean
  client_is_in_carbure: boolean
}

export type Lots = {
  from: number
  returned: number
  total: number
  lots: Lot[]
}

export enum Filters {
  MatieresPremieres = "matieres_premieres",
  Biocarburants = "biocarburants",
  Periods = "periods",
  ProductionSites = "production_sites",
  CountriesOfOrigin = "countries_of_origin",
  Clients = "clients",
}

export interface ApiFilters {
  matieres_premieres: Option[]
  biocarburants: Option[]
  countries_of_origin: Option[]
  periods: string[]
  production_sites: string[]
  clients: string[]
}

export type Snapshot = {
  lots: {
    [key in LotStatus]: number
  }

  filters: {
    [key in Filters]: Option[]
  }

  deadlines: any[]
}

export type Entity = {
  id: number
  name: string
  entity_type: string
}

export type Settings = {
  email: string
  rights: { entity: Entity }[]
}
