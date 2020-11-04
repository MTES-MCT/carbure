import {
  Biocarburant,
  Country,
  DeliverySite,
  Entity,
  Transaction,
  MatierePremiere,
  ProductionSite,
} from "../../services/types"
import { EntitySelection } from "./use-entity"

import useForm, { FormHook } from "./use-form"

export interface TransactionFormState {
  id: number
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

  producer_is_in_carbure: boolean
  carbure_producer: Entity | null
  unknown_producer: string
  carbure_production_site: ProductionSite | null
  unknown_production_site: string
  unknown_production_country: Country | null
  unknown_production_site_com_date: string
  unknown_production_site_reference: string
  unknown_production_site_dbl_counting: string

  client_is_in_carbure: boolean
  carbure_client: Entity | null
  unknown_client: string

  delivery_site_is_in_carbure: boolean
  carbure_delivery_site: DeliverySite | null
  unknown_delivery_site: string
  unknown_delivery_site_country: Country | null
}

export function toTransactionFormState(tx: Transaction): TransactionFormState {
  return {
    id: tx.id,
    dae: tx.dae,
    volume: tx.lot.volume,
    champ_libre: tx.champ_libre,
    delivery_date: tx.delivery_date,
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
    unknown_production_site: tx.lot.unknown_production_site,
    unknown_production_site_reference: tx.lot.unknown_production_site_reference,
    unknown_production_site_com_date:
      tx.lot.unknown_production_site_com_date ?? "",
    unknown_production_site_dbl_counting:
      tx.lot.unknown_production_site_dbl_counting,

    client_is_in_carbure: tx.client_is_in_carbure,
    carbure_client: tx.carbure_client,
    unknown_client: tx.unknown_client,

    delivery_site_is_in_carbure: tx.delivery_site_is_in_carbure,
    carbure_delivery_site: tx.carbure_delivery_site,
    unknown_delivery_site: tx.unknown_delivery_site,
    unknown_delivery_site_country: tx.unknown_delivery_site_country,
  }
}

export function toTransactionPostData(tx: TransactionFormState) {
  return {
    volume: tx.volume,
    dae: tx.dae,
    champ_libre: tx.champ_libre,
    delivery_date: tx.delivery_date,
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
    production_site_reference: !tx.producer_is_in_carbure
      ? tx.unknown_production_site_reference
      : "",
    production_site_commissioning_date: !tx.producer_is_in_carbure
      ? tx.unknown_production_site_com_date
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
      ? tx.unknown_delivery_site_country
      : "",
  }
}

// empty form state
const initialState: TransactionFormState = {
  id: -1,
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

  producer_is_in_carbure: true,
  carbure_producer: null,
  unknown_producer: "",

  carbure_production_site: null,
  unknown_production_site: "",
  unknown_production_country: null,
  unknown_production_site_com_date: "",
  unknown_production_site_reference: "",
  unknown_production_site_dbl_counting: "",

  client_is_in_carbure: true,
  carbure_client: null,
  unknown_client: "",

  delivery_site_is_in_carbure: true,
  carbure_delivery_site: null,
  unknown_delivery_site: "",
  unknown_delivery_site_country: null,
}

export default function useTransactionForm(
  entity: EntitySelection
): FormHook<TransactionFormState> {
  const [form, hasChange, onChange, setForm] = useForm<TransactionFormState>(
    initialState
  )

  const isProducer = entity?.entity_type === "Producteur"
  const isOperator = entity?.entity_type === "Opérateur"

  if (isProducer && form.carbure_producer?.id !== entity?.id) {
    setForm({
      ...form,
      producer_is_in_carbure: true,
      carbure_producer: entity,
    })
  }

  if (isOperator && form.carbure_client?.id !== entity?.id) {
    setForm({
      ...form,
      client_is_in_carbure: true,
      carbure_client: entity,
    })
  }

  return [form, hasChange, onChange, setForm]
}
