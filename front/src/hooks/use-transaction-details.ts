import { useParams } from "react-router-dom"

import {
  Biocarburant,
  Country,
  DeliverySite,
  Entity,
  Lot,
  Lots,
  MatierePremiere,
  ProductionSite,
} from "../services/types"

import useForm, { FormFields } from "./use-form"

export interface TransactionFormState {
  id: number
  dae: string
  volume: number
  champ_libre: string
  delivery_date: string
  mac: boolean
  pays_origine: Country

  eec: number
  el: number
  ep: number
  etd: number
  eu: number
  esca: number
  eccs: number
  eccr: number
  eee: number

  biocarburant: Biocarburant
  matiere_premiere: MatierePremiere

  producer_is_in_carbure: boolean
  carbure_producer: Entity | null
  unknown_producer: string | null
  unknown_production_country: string | null

  production_site_is_in_carbure: boolean
  carbure_production_site: ProductionSite | null
  unknown_production_site: string | null
  unknown_production_site_com_date: string | null
  // unknown_production_site_dbl_counting: string | null
  unknown_production_site_reference: string | null

  client_is_in_carbure: boolean
  client: Entity | null
  unknown_client: string | null

  delivery_site_is_on_carbure: boolean
  delivery_site: DeliverySite | null
  delivery_site_country: string
}

function extractFormData(tr: Lot): TransactionFormState {
  return {
    id: tr.lot.id,
    dae: tr.dae,
    volume: tr.lot.volume,
    champ_libre: tr.champ_libre,
    delivery_date: tr.delivery_date,
    mac: tr.is_mac,
    pays_origine: tr.lot.pays_origine,

    eec: tr.lot.eec,
    el: tr.lot.el,
    ep: tr.lot.ep,
    etd: tr.lot.etd,
    eu: tr.lot.eu,
    esca: tr.lot.esca,
    eccs: tr.lot.eccs,
    eccr: tr.lot.eccr,
    eee: tr.lot.eee,

    biocarburant: tr.lot.biocarburant,
    matiere_premiere: tr.lot.matiere_premiere,

    producer_is_in_carbure: tr.lot.producer_is_in_carbure,
    carbure_producer: tr.lot.carbure_producer,
    unknown_producer: tr.lot.unknown_producer,
    unknown_production_country: tr.lot.unknown_production_country,

    production_site_is_in_carbure: tr.lot.production_site_is_in_carbure,
    carbure_production_site: tr.lot.carbure_production_site,
    unknown_production_site: tr.lot.unknown_production_site,
    unknown_production_site_reference: tr.lot.unknown_production_site_reference,
    unknown_production_site_com_date:
      tr.lot.unknown_production_site_com_date ?? "2020-09-21", //@TODO fill this correctly somewhere, otherwise API crash

    client_is_in_carbure: tr.client_is_in_carbure,
    client: tr.carbure_client,
    unknown_client: tr.unknown_client,

    delivery_site_is_on_carbure: tr.delivery_site_is_in_carbure,
    delivery_site: tr.carbure_delivery_site,
    delivery_site_country:
      tr.carbure_delivery_site?.country.code_pays ??
      tr.unknown_delivery_site_country,
  }
}

export type TransactionDetailsHook = [
  TransactionFormState | null,
  <T extends FormFields>(e: React.ChangeEvent<T>) => void
]

export default function useTransactionDetails(
  transactions: Lots | null
): TransactionDetailsHook {
  const params: { id: string } = useParams()
  const [form, onChange, setForm] = useForm<TransactionFormState | null>(null)

  if (transactions) {
    const transactionID = parseInt(params.id, 10)

    // find the relevant lot
    // @TODO would be nice to be able to fetch details for only one lot
    const transaction = transactions.lots.find(
      (lot) => lot.lot.id === transactionID
    )

    // initialize the form with data coming from the loaded transaction
    if (transaction && form === null) {
      setForm(extractFormData(transaction))
    }
  }

  return [form, onChange]
}
