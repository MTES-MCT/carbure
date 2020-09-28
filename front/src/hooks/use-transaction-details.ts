import { useParams } from "react-router-dom"

import useForm, { FormFields } from "./use-form"
import { Lot, Lots } from "../services/types"

export interface TransactionFormState {
  id: number
  biocarburant_code: string
  matiere_premiere_code: string
  pays_origine_code: string
  producer: string
  production_site: string
  production_site_country: string
  production_site_reference: string
  production_site_commissioning_date: string
  volume: number
  eec: number
  el: number
  ep: number
  etd: number
  eu: number
  esca: number
  eccs: number
  eccr: number
  eee: number
  dae: string
  champ_libre: string
  client: string
  delivery_date: string
  delivery_site: string
  delivery_site_country: string
  mac: boolean
}

function extractFormData(tr: Lot): TransactionFormState {
  return {
    id: tr.lot.id,
    biocarburant_code: tr.lot.biocarburant.code,
    matiere_premiere_code: tr.lot.matiere_premiere.code,
    pays_origine_code: tr.lot.pays_origine.code_pays,
    producer:
      tr.lot.carbure_producer?.id.toString() ?? tr.lot.unknown_producer ?? "",
    production_site:
      tr.lot.carbure_production_site?.id.toString() ??
      tr.lot.unknown_production_site ??
      "",
    production_site_country: tr.lot.carbure_production_site.country.code_pays,
    production_site_reference: tr.lot.unknown_production_site_reference ?? "",
    production_site_commissioning_date:
      tr.lot.unknown_production_site_com_date ?? "",
    volume: tr.lot.volume,
    eec: tr.lot.eec,
    el: tr.lot.el,
    ep: tr.lot.ep,
    etd: tr.lot.etd,
    eu: tr.lot.eu,
    esca: tr.lot.esca,
    eccs: tr.lot.eccs,
    eccr: tr.lot.eccr,
    eee: tr.lot.eee,
    dae: tr.dae,
    champ_libre: tr.champ_libre,
    client: tr.carbure_client?.id ?? tr.unknown_client ?? "",
    delivery_date: tr.delivery_date,
    delivery_site:
      tr.carbure_delivery_site?.id ?? tr.unknown_delivery_site ?? "",
    delivery_site_country:
      tr.carbure_delivery_site?.country.code_pays ??
      tr.unknown_delivery_site_country,
    mac: tr.is_mac,
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
