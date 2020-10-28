import { Transaction, Lots, LotStatus, Snapshot, StockSnapshot } from "./types"
import { FilterSelection } from "../hooks/query/use-filters"
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
    delivery_sites: snapshot.filters.delivery_sites.map(toOption),
  }

  snapshot.years = snapshot.years.map(toOption)

  return snapshot
}

function toTransactionPostData(tx: TransactionFormState) {
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
      ? tx.unknown_production_country
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

// extract the status name from the lot details
export function getStatus(transaction: Transaction, entity: number): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  const isProducer = transaction.carbure_vendor?.id === entity
  const isOperator = transaction.carbure_client?.id === entity

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (delivery === "A") {
      return LotStatus.Accepted
    }
    // OPERATEUR
    else if (isOperator && ["N", "AA", "AC"].includes(delivery)) {
      return LotStatus.Inbox
    }
    // PRODUCTEUR
    else if (isProducer) {
      if (["N", "AA"].includes(delivery)) {
        return LotStatus.Validated
      } else if (["AC", "R"].includes(delivery)) {
        return LotStatus.ToFix
      }
    }
  }

  return LotStatus.Weird
}

function normalizeStatus(transactions: any, entityID: number) {
  transactions.lots.forEach((tx: any) => {
    tx.status = getStatus(tx, entityID)
  })

  return transactions
}

export function getSnapshot(entityID: number, year: number): Promise<Snapshot> {
  return api
    .get("/lots/snapshot", { entity_id: entityID, year })
    .then(normalizeFilters)
}

export function getLots(
  status: LotStatus,
  entityID: number,
  filters: FilterSelection["selected"],
  year: number,
  page: number,
  limit: number,
  query: string,
  sortBy: string,
  order: string,
  invalid: boolean,
  deadline: boolean
): Promise<Lots> {
  const params = {
    ...filters,
    entity_id: entityID,
    from_idx: page * limit,
    sort_by: sortBy,
    status,
    year,
    limit,
    query,
    order,
    invalid,
    deadline,
  }

  return api.get("/lots", params).then((txs) => normalizeStatus(txs, entityID))
}

export function downloadLots(
  status: LotStatus,
  producerID: number,
  filters: FilterSelection["selected"],
  year: number,
  query: string,
  sortBy: string,
  order: string
) {
  return api.download("/lots", {
    ...filters,
    entity_id: producerID,
    sort_by: sortBy,
    status,
    year,
    query,
    order,
    export: true,
  })
}

export function addLot(entityID: number, params: any): Promise<Transaction> {
  return api.post("/lots/add", {
    entity_id: entityID,
    ...toTransactionPostData(params),
  })
}

export function uploadLotFile(entityID: number, file: File): Promise<void> {
  return api.post("/lots/upload", {
    entity_id: entityID,
    file,
  })
}

export function updateLot(
  entityID: number,
  transactionID: number,
  params: any
): Promise<Transaction> {
  return api.post("/lots/update", {
    entity_id: entityID,
    tx_id: transactionID,
    ...toTransactionPostData(params),
  })
}

export function duplicateLot(entityID: number, transactionID: number) {
  return api.post("/lots/duplicate", {
    entity_id: entityID,
    tx_id: transactionID,
  })
}

export function deleteLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/delete", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function validateLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/validate", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function acceptLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/accept", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function rejectLots(
  entityID: number,
  transactionIDs: number[],
  comment: string
) {
  return api.post("/lots/reject", {
    entity_id: entityID,
    tx_ids: transactionIDs,
    comment,
  })
}

export function commentLot(
  entityID: number,
  transactionID: number,
  comment: string
) {
  return api.post("/lots/comment", {
    entity_id: entityID,
    tx_id: transactionID,
    comment,
    comment_type: "BOTH",
  })
}

export function acceptAndCommentLot(
  entityID: number,
  transactionID: number,
  comment: string
) {
  const accepting = acceptLots(entityID, [transactionID])
  const commenting = commentLot(entityID, transactionID, comment)

  return Promise.all([accepting, commenting])
}

export function deleteAllDraftLots(entityID: number, year: number) {
  return api.post("/lots/delete-all-drafts", {
    entity_id: entityID,
    year,
  })
}

export function validateAllDraftLots(entityID: number, year: number) {
  return api.post("/lots/validate-all-drafts", {
    entity_id: entityID,
    year,
  })
}

export function acceptAllInboxLots(entityID: number, year: number) {
  return api.post("/lots/accept-all", {
    entity_id: entityID,
    year,
  })
}

export function rejectAllInboxLots(
  entityID: number,
  year: number,
  comment: string
) {
  return api.post("/lots/reject-all", {
    entity_id: entityID,
    year,
    comment,
  })
}

export function getLotsOutSummary(entityID: number) {
  return api.get("/lots/summary-out", {
    entity_id: entityID,
  })
}

export function getLotsInSummary(entityID: number) {
  return api.get("/lots/summary-in", {
    entity_id: entityID,
  })
}

// give the same type to all filters in order to render them easily
function normalizeStockSnapshotFilters(snapshot: any): StockSnapshot {
  snapshot.filters = {
    matieres_premieres: snapshot.filters.matieres_premieres,
    biocarburants: snapshot.filters.biocarburants,
    countries_of_origin: snapshot.filters.countries_of_origin,
    production_sites: snapshot.filters.production_sites.map(toOption),
    delivery_sites: snapshot.filters.delivery_sites.map(toOption),
  }
  return snapshot
}

export function getStockSnapshot(entity_id: number): Promise<StockSnapshot> {
  return api
    .get("/stocks/snapshot", { entity_id })
    .then(normalizeStockSnapshotFilters)
}

export function getStocks(
  entityID: number,
  filters: FilterSelection["selected"],
  page: number,
  limit: number,
  query: string,
  sortBy: string,
  order: string
): Promise<Lots> {
  return api.get("/stocks", {
    ...filters,
    entity_id: entityID,
    from_idx: page * limit,
    sort_by: sortBy,
    limit,
    query,
    order,
  })
}
