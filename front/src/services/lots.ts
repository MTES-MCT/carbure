import { Transaction, Lots, LotStatus, Snapshot } from "./types"
import { FilterSelection } from "../hooks/use-transactions"
import { TransactionFormState } from "../hooks/helpers/use-transaction-form"

import api from "./api"

function toOption(value: string) {
  return { value, label: value }
}

// give the same type to all filters in order to render them easily
function normalizeFilters(snapshot: any): Snapshot {
  snapshot.filters = {
    matieres_premieres: snapshot.filters.matieres_premieres,
    biocarburants: snapshot.filters.biocarburants,
    countries_of_origin: snapshot.filters.countries_of_origin,
    periods: snapshot.filters.periods.map(toOption),
    production_sites: snapshot.filters.production_sites.map(toOption),
    clients: snapshot.filters.clients.map(toOption),
  }

  return snapshot
}

export function toTransactionPostData(tx: TransactionFormState) {
  return {
    biocarburant_code: tx.biocarburant?.code,
    matiere_premiere_code: tx.matiere_premiere?.code,
    pays_origine_code: tx.pays_origine?.code_pays,
    producer: tx.carbure_producer?.name ?? tx.unknown_producer,
    production_site:
      tx.carbure_production_site?.name ?? tx.unknown_production_site,
    production_site_country: tx.unknown_production_country,
    production_site_reference: tx.unknown_production_site_reference,
    production_site_commissioning_date: tx.unknown_production_site_com_date,
    double_counting_registration: tx.unknown_production_site_dbl_counting,
    volume: tx.volume,
    eec: tx.eec,
    el: tx.el,
    ep: tx.ep,
    etd: tx.etd,
    eu: tx.eu,
    esca: tx.esca,
    eccs: tx.eccs,
    eccr: tx.eccr,
    eee: tx.eee,
    dae: tx.dae,
    champ_libre: tx.champ_libre,
    client: tx.carbure_client?.name ?? tx.unknown_client,
    delivery_date: tx.delivery_date,
    delivery_site: tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site,
    delivery_site_country: tx.unknown_delivery_site_country,
    mac: tx.mac,
  }
}

// extract the status name from the lot details
export function getStatus(lot: Transaction): LotStatus {
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

export function getSnapshot(producer_id: number): Promise<Snapshot> {
  return api.get("/lots/snapshot", { producer_id }).then(normalizeFilters)
}

export function getLots(
  status: LotStatus,
  producerID: number,
  filters: FilterSelection["selected"],
  page: number,
  limit: number
): Promise<Lots> {
  return api.get("/lots", {
    status,
    producer_id: producerID,
    ...filters,
    from_idx: page * limit,
    limit: limit,
  })
}

export function addLots(entityID: number, params: any): Promise<Transaction> {
  return api.post("/lots/add", {
    entity_id: entityID,
    ...toTransactionPostData(params),
  })
}
