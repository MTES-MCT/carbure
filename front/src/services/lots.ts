import api, { ApiResponse } from "./api"

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

export type Filter = {
  key: string
  label: string
}

export enum Filters {
  MatieresPremieres = "matieres_premieres",
  Biocarburants = "biocarburants",
  Periods = "periods",
  ProductionSites = "production_sites",
  CountriesOfOrigin = "countries_of_origin",
  Clients = "clients",
}

export type Snapshot = {
  lots: {
    [LotStatus.Draft]: number
    [LotStatus.Validated]: number
    [LotStatus.ToFix]: number
    [LotStatus.Accepted]: number
    [LotStatus.Weird]: number
  }

  filters: {
    [Filters.MatieresPremieres]: Filter[]
    [Filters.Biocarburants]: Filter[]
    [Filters.Periods]: Filter[]
    [Filters.ProductionSites]: Filter[]
    [Filters.CountriesOfOrigin]: Filter[]
    [Filters.Clients]: Filter[]
  }

  deadlines: any[]
}

// extract the status name from the lot details
export function getStatus(lot: Lot): LotStatus {
  const status = lot.lot.status.toLowerCase()
  const delivery = lot.delivery_status

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (["N", "AA"].includes(delivery)) {
      return LotStatus.Validated
    } else if (delivery === "AC") {
      return LotStatus.ToFix
    } else if (delivery === "A") {
      return LotStatus.Accepted
    }
  }

  return LotStatus.Weird
}

export function getLots(
  status: LotStatus,
  producerID: number,
  filters: any,
  from: number,
  limit: number
): ApiResponse<Lots> {
  return api.get("/lots", {
    status,
    producer_id: producerID,
    ...filters,
    from_idx: from * limit,
    limit,
  })
}

export function getSnapshot(producerID: number): ApiResponse<Snapshot> {
  return api.get("/lots/snapshot", { producer_id: producerID })
}
