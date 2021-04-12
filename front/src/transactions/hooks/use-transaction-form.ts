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
} from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import useForm, { FormHook } from "common/hooks/use-form"

export interface TransactionFormState {
  id: number
  carbure_id: string
  dae: string
  volume: number
  champ_libre: string
  delivery_date: string
  mac: boolean
  status: string

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

  producer_is_in_carbure: boolean
  carbure_producer: Entity | null
  unknown_producer: string
  carbure_production_site: ProductionSiteDetails | null
  carbure_production_site_reference: string
  unknown_production_site: string
  unknown_production_country: Country | null
  unknown_production_site_com_date: string
  unknown_production_site_reference: string
  unknown_production_site_dbl_counting: string | null

  carbure_vendor: Entity | null
  carbure_vendor_certificate: string
  unknown_supplier: string
  unknown_supplier_certificate: string

  client_is_in_carbure: boolean
  carbure_client: Entity | null
  unknown_client: string

  delivery_site_is_in_carbure: boolean
  carbure_delivery_site: DeliverySite | null
  unknown_delivery_site: string
  unknown_delivery_site_country: Country | null

  added_by: Entity | null
}

export function toTransactionFormState(tx: Transaction): TransactionFormState {
  return {
    id: tx.id,
    status: tx.lot.status,
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

    producer_is_in_carbure: tx.lot.producer_is_in_carbure,
    carbure_producer: tx.lot.carbure_producer,
    unknown_producer: tx.lot.unknown_producer,
    unknown_production_country: tx.lot.unknown_production_country,

    carbure_production_site: tx.lot.carbure_production_site,
    carbure_production_site_reference: tx.lot.carbure_production_site_reference,
    unknown_production_site: tx.lot.unknown_production_site,
    unknown_production_site_reference: tx.lot.unknown_production_site_reference,
    unknown_production_site_com_date:
      tx.lot.unknown_production_site_com_date ?? "",
    unknown_production_site_dbl_counting:
      tx.lot.unknown_production_site_dbl_counting,

    carbure_vendor: tx.carbure_vendor,
    carbure_vendor_certificate: tx.carbure_vendor_certificate,

    unknown_supplier: tx.lot.unknown_supplier ?? "",
    unknown_supplier_certificate: tx.lot.unknown_supplier_certificate,

    client_is_in_carbure: tx.client_is_in_carbure,
    carbure_client: tx.carbure_client,
    unknown_client: tx.unknown_client,

    delivery_site_is_in_carbure: tx.delivery_site_is_in_carbure,
    carbure_delivery_site: tx.carbure_delivery_site,
    unknown_delivery_site: tx.unknown_delivery_site,
    unknown_delivery_site_country: tx.unknown_delivery_site_country,

    added_by: tx.lot.added_by,
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

    producer: tx.producer_is_in_carbure
      ? tx.carbure_producer?.name
      : tx.unknown_producer,

    production_site: tx.producer_is_in_carbure
      ? tx.carbure_production_site?.name
      : tx.unknown_production_site,

    production_site_country: !tx.producer_is_in_carbure
      ? tx.unknown_production_country?.code_pays
      : "",

    production_site_reference: tx.producer_is_in_carbure
      ? tx.carbure_production_site_reference
      : tx.unknown_production_site_reference,

    production_site_commissioning_date: !tx.producer_is_in_carbure
      ? excelDate(tx.unknown_production_site_com_date)
      : "",

    double_counting_registration: !tx.producer_is_in_carbure
      ? tx.unknown_production_site_dbl_counting
      : "",

    client: tx.client_is_in_carbure
      ? tx.carbure_client?.name
      : tx.unknown_client,

    delivery_site: tx.delivery_site_is_in_carbure
      ? tx.carbure_delivery_site?.depot_id
      : tx.unknown_delivery_site,

    delivery_site_country: !tx.delivery_site_is_in_carbure
      ? tx.unknown_delivery_site_country?.code_pays
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
  dae: "",
  volume: 0,
  champ_libre: "",
  delivery_date: "",
  mac: false,
  pays_origine: null,
  status: "Draft",

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

  producer_is_in_carbure: true,
  carbure_producer: null,
  unknown_producer: "",

  carbure_production_site: null,
  carbure_production_site_reference: "",
  unknown_production_site: "",
  unknown_production_country: null,
  unknown_production_site_com_date: "",
  unknown_production_site_reference: "",
  unknown_production_site_dbl_counting: "",

  carbure_vendor: null,
  carbure_vendor_certificate: "",

  unknown_supplier: "",
  unknown_supplier_certificate: "",

  client_is_in_carbure: true,
  carbure_client: null,
  unknown_client: "",

  delivery_site_is_in_carbure: true,
  carbure_delivery_site: null,
  unknown_delivery_site: "",
  unknown_delivery_site_country: null,

  added_by: null,
}

// fixed values (only for drafts)
function fixedValues(
  tx: TransactionFormState,
  entity: EntitySelection
): TransactionFormState {
  if (entity === null) return tx

  // for producers
  if (entity.entity_type === EntityType.Producer) {
    tx.carbure_producer = entity
    tx.carbure_vendor = entity

    // no trading => producer can only be entity
    if (!entity.has_trading) {
      tx.producer_is_in_carbure = true
    }
  }

  // for operators
  if (entity.entity_type === EntityType.Operator) {
    tx.client_is_in_carbure = true
    tx.carbure_client = entity

    // no mac => client can only be entity
    if (!entity.has_mac) {
      tx.client_is_in_carbure = true
    }
  }

  // for traders
  if (entity.entity_type === EntityType.Trader) {
    tx.producer_is_in_carbure = false
    tx.carbure_vendor = entity
  }

  // if transaction is mac
  if (tx.mac) {
    tx.client_is_in_carbure = false
    tx.delivery_site_is_in_carbure = false
  }

  // update GES summary
  tx.ghg_total = tx.eec + tx.el + tx.ep + tx.etd + tx.eu - tx.esca - tx.eccs - tx.eccr - tx.eee // prettier-ignore
  tx.ghg_reduction = (1.0 - tx.ghg_total / tx.ghg_reference) * 100.0

  return tx
}

export default function useTransactionForm(
  entity: EntitySelection,
  isStock: boolean = false
): FormHook<TransactionFormState> {
  const onChange = useCallback(
    (state: TransactionFormState) => {
      if (isStock || entity === null || state.status !== "Draft") return state
      else return fixedValues(state, entity)
    },
    [isStock, entity]
  )

  return useForm<TransactionFormState>(initialState, { onChange })
}
