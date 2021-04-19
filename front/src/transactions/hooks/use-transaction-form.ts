import { useCallback } from "react"
import format from "date-fns/format"

import {
  Biocarburant,
  Country,
  DeliverySite,
  Entity,
  Transaction,
  MatierePremiere,
  ProductionSiteDetails,
  EntityType,
  Lot,
} from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import useForm, { FormHook } from "common/hooks/use-form"

export interface TransactionFormState {
  id: number
  carbure_id: string
  status: string
  delivery_status: string
  added_by: Entity | null
  parent_lot: Lot | null

  dae: string
  volume: number
  champ_libre: string
  delivery_date: string
  mac: boolean

  eec: number
  el: number
  ep: number
  etd: number
  eu: number
  esca: number
  eccs: number
  eccr: number
  eee: number

  ghg_total: number
  ghg_reduction: number
  ghg_reference: number

  biocarburant: Biocarburant | null
  matiere_premiere: MatierePremiere | null
  pays_origine: Country | null

  producer: Entity | string | null
  unknown_supplier: string | null
  unknown_supplier_certificate: string | null
  production_site: ProductionSiteDetails | string | null
  production_site_reference: string
  production_site_country: Country | null
  production_site_com_date: string
  production_site_dbl_counting: string | null

  carbure_vendor: Entity | null
  carbure_vendor_certificate: string

  client: Entity | string | null

  delivery_site: DeliverySite | string | null
  delivery_site_country: Country | null
}

export function toTransactionFormState(tx: Transaction): TransactionFormState {
  return {
    id: tx.id,
    status: tx.lot.status,
    delivery_status: tx.delivery_status,
    carbure_id: tx.lot.carbure_id,
    dae: tx.dae,
    volume: tx.lot.volume,
    champ_libre: tx.champ_libre,
    delivery_date: tx.delivery_date ?? "",
    mac: tx.is_mac,

    eec: tx.lot.eec,
    el: tx.lot.el,
    ep: tx.lot.ep,
    etd: tx.lot.etd,
    eu: tx.lot.eu,
    esca: tx.lot.esca,
    eccs: tx.lot.eccs,
    eccr: tx.lot.eccr,
    eee: tx.lot.eee,

    ghg_total: tx.lot.ghg_total,
    ghg_reduction: tx.lot.ghg_reduction,
    ghg_reference: tx.lot.ghg_reference,

    biocarburant: tx.lot.biocarburant,
    matiere_premiere: tx.lot.matiere_premiere,
    pays_origine: tx.lot.pays_origine,

    producer: tx.lot.producer_is_in_carbure
      ? tx.lot.carbure_producer
      : tx.lot.unknown_producer,

    production_site: tx.lot.production_site_is_in_carbure
      ? tx.lot.carbure_production_site
      : tx.lot.unknown_production_site,

    production_site_country: tx.lot.production_site_is_in_carbure
      ? tx.lot.carbure_production_site?.country ?? null
      : tx.lot.unknown_production_country,

    production_site_reference: tx.lot.production_site_is_in_carbure
      ? tx.lot.carbure_production_site_reference
      : tx.lot.unknown_production_site_reference,

    production_site_com_date: tx.lot.production_site_is_in_carbure
      ? tx.lot.carbure_production_site?.date_mise_en_service ?? ""
      : tx.lot.unknown_production_site_com_date ?? "",

    production_site_dbl_counting: tx.lot.production_site_is_in_carbure
      ? tx.lot.carbure_production_site?.dc_reference ?? null
      : tx.lot.unknown_production_site_dbl_counting,

    carbure_vendor: tx.carbure_vendor,
    carbure_vendor_certificate: tx.carbure_vendor_certificate,

    unknown_supplier: tx.lot.unknown_supplier ?? "",
    unknown_supplier_certificate: tx.lot.unknown_supplier_certificate,

    client: tx.client_is_in_carbure ? tx.carbure_client : tx.unknown_client,

    delivery_site: tx.delivery_site_is_in_carbure
      ? tx.carbure_delivery_site
      : tx.unknown_delivery_site,

    delivery_site_country: tx.delivery_site_is_in_carbure
      ? tx.carbure_delivery_site?.country ?? null
      : tx.unknown_delivery_site_country,

    added_by: tx.lot.added_by,
    parent_lot: tx.lot.parent_lot,
  }
}

function excelDate(value: string) {
  try {
    const date = new Date(value)
    const formatted = format(date, "dd/MM/yyyy")
    return formatted
  } catch (e) {
    return null
  }
}

export function toTransactionPostData(tx: TransactionFormState) {
  return {
    volume: tx.volume,
    dae: tx.dae,
    champ_libre: tx.champ_libre,
    delivery_date: excelDate(tx.delivery_date),
    mac: tx.mac,

    eec: tx.eec,
    el: tx.el,
    ep: tx.ep,
    etd: tx.etd,
    eu: tx.eu,
    esca: tx.esca,
    eccs: tx.eccs,
    eccr: tx.eccr,
    eee: tx.eee,

    biocarburant_code: tx.biocarburant?.code,
    matiere_premiere_code: tx.matiere_premiere?.code,
    pays_origine_code: tx.pays_origine?.code_pays,

    producer: typeof tx.producer === "string" ? tx.producer : tx.producer?.name,

    production_site:
      typeof tx.production_site === "string"
        ? tx.production_site
        : tx.production_site?.name,

    production_site_country: tx.production_site_country?.code_pays,

    production_site_reference: tx.production_site_reference,

    production_site_commissioning_date:
      typeof tx.production_site === "string"
        ? excelDate(tx.production_site_com_date)
        : "",

    double_counting_registration:
      typeof tx.production_site === "string"
        ? tx.production_site_dbl_counting
        : "",

    client: typeof tx.client === "string" ? tx.client : tx.client?.name,

    delivery_site:
      typeof tx.delivery_site === "string"
        ? tx.delivery_site
        : tx.delivery_site?.depot_id,

    delivery_site_country:
      typeof tx.delivery_site === "string"
        ? tx.delivery_site_country?.code_pays
        : "",

    vendor: tx.carbure_vendor?.name ?? "",
    vendor_certificate: tx.carbure_vendor_certificate,

    supplier: tx.unknown_supplier,
    supplier_certificate: tx.unknown_supplier_certificate,
  }
}

// empty form state
const initialState: TransactionFormState = {
  id: -1,
  carbure_id: "",
  added_by: null,
  parent_lot: null,
  status: "Draft",
  delivery_status: "N",

  dae: "",
  volume: 0,
  champ_libre: "",
  delivery_date: "",
  mac: false,
  pays_origine: null,

  eec: 0,
  el: 0,
  ep: 0,
  etd: 0,
  eu: 0,
  esca: 0,
  eccs: 0,
  eccr: 0,
  eee: 0,

  ghg_total: 0,
  ghg_reduction: 0,
  ghg_reference: 83.8,

  biocarburant: null,
  matiere_premiere: null,

  producer: null,

  production_site: null,
  production_site_reference: "",
  production_site_country: null,
  production_site_com_date: "",
  production_site_dbl_counting: "",

  carbure_vendor: null,
  carbure_vendor_certificate: "",

  unknown_supplier: "",
  unknown_supplier_certificate: "",

  client: null,

  delivery_site: null,
  delivery_site_country: null,
}

// fixed values (only for drafts)
function fixedValues(
  tx: TransactionFormState,
  prevTx: TransactionFormState | undefined,
  entity: Entity
): TransactionFormState {
  if (entity === null) return tx
  if (tx.status !== "Draft") return tx

  // for producers
  if (entity.entity_type === EntityType.Producer) {
    tx.carbure_vendor = entity

    if (!entity.has_trading) {
      tx.producer = entity
    }
  }

  // for operators
  if (entity.entity_type === EntityType.Operator && !tx.mac) {
    tx.client = entity
  }

  // for traders
  if (entity.entity_type === EntityType.Trader) {
    tx.carbure_vendor = entity
  }

  if (!prevTx?.mac && tx.mac) {
    tx.delivery_site = ""
    tx.delivery_site_country = null
  }

  // update GES summary
  tx.ghg_total = tx.eec + tx.el + tx.ep + tx.etd + tx.eu - tx.esca - tx.eccs - tx.eccr - tx.eee // prettier-ignore
  tx.ghg_reduction = (1.0 - tx.ghg_total / tx.ghg_reference) * 100.0

  return tx
}

export type TransactionFields = Record<string, boolean>

export default function useTransactionForm(
  entity: EntitySelection,
  isStock: boolean = false
): FormHook<TransactionFormState> {
  const onChange = useCallback(
    (state, prevState) => {
      if (isStock || entity === null || state.status !== "Draft") return state
      else return fixedValues(state, prevState, entity)
    },
    [isStock, entity]
  )

  return useForm<TransactionFormState>(initialState, { onChange })
}
