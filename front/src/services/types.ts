import { Option } from "../components/system/select"

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
}

export interface Entity {
  id: number
  name: string
  entity_type: string
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

export interface DeliverySite {
  name: string
  city: string
  depot_id: string
  country: Country
  depot_type?: string
}

export interface ProductionSite {
  id: number
  name: string
  country: Country
  date_mise_en_service: string
}

export interface ProductionSiteDetails extends ProductionSite {
  date_mise_en_service: string
  ges_option: string
  eligible_dc: boolean
  dc_reference: null // @TODO
  inputs: MatierePremiere[]
  outputs: Biocarburant[]
  producer: Entity
}

export interface Lot {
  id: number
  carbure_id: string
  volume: number
  period: string
  source: string
  status: LotStatus
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
  carbure_producer: Entity
  unknown_producer: string

  production_site_is_in_carbure: boolean
  carbure_production_site: ProductionSite
  unknown_production_site: string
  unknown_production_country: Country
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
  delivery_status: string
  delivery_date: string
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
  unknown_delivery_site_country: Country
}

export interface Lots {
  from: number
  returned: number
  total: number
  lots: Transaction[]

  tx_errors: {
    [key: string]: {
      tx_id: number
      field: string
      value: string
      error: string
    }[]
  }

  lots_errors: {
    [key: string]: {
      lot_id: number
      field: string
      value: string
      error: string
    }[]
  }
}

export enum Filters {
  MatieresPremieres = "matieres_premieres",
  Biocarburants = "biocarburants",
  Periods = "periods",
  ProductionSites = "production_sites",
  CountriesOfOrigin = "countries_of_origin",
  Clients = "clients",
}

export interface Snapshot {
  lots: {
    [key in LotStatus]: number
  }

  filters: {
    [key in Filters]: Option[]
  }

  deadlines: any[]

  years: Option[]
}

export interface Settings {
  email: string
  rights: { entity: Entity }[]
}

export interface StockSnapshot {
  filters: {
    [key in Filters]: Option[]
  }
}