import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

import {
  Filters,
  Snapshot,
  Transaction,
  LotStatus,
  SummaryItem,
  GenericError,
  TransactionSummary,
} from "common/types"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { Option } from "common/components/select"
import { TFunction } from "react-i18next"

export function toOption(value: string): Option {
  return { value, label: value }
}

export function hasDeadline(tx: Transaction, deadline: string): boolean {
  if (!tx || tx.lot.status !== "Draft") return false

  const deadlineDate = new Date(deadline)

  const deliveryDate = tx?.delivery_date
    ? new Date(tx.delivery_date)
    : new Date()

  return differenceInCalendarMonths(deadlineDate, deliveryDate) === 1
}

export function hasWarnings(
  tx: Transaction,
  errors: Record<number, GenericError[]>
): boolean {
  if (!tx || !errors[tx.id]) return false
  return errors[tx.id].every((e) => !e.is_blocking)
}

export function hasErrors(
  tx: Transaction,
  errors: Record<number, GenericError[]>
): boolean {
  if (!tx || !errors[tx.id]) return false
  return errors[tx.id].some((e) => e.is_blocking)
}

// give the same interface to all filters in order to render them easily
export function normalizeFilter(
  field: Filters,
  filter: string[] | Option[],
  t: TFunction
): Option[] {
  let normalized: Option[] = []

  if (filter && typeof filter[0] === "string") {
    const set = new Set<string>(filter as string[])
    normalized = Array.from(set).map(toOption)
  }

  if (field === Filters.Biocarburants) {
    normalized = filter.map((bc: any) => ({
      value: bc.value,
      label: t(bc.value, { ns: "biofuels" }),
    }))
  }

  if (field === Filters.MatieresPremieres) {
    normalized = filter.map((mp: any) => ({
      value: mp.value,
      label: t(mp.value, { ns: "feedstocks" }),
    }))
  }

  if (field === Filters.CountriesOfOrigin) {
    normalized = filter.map((ct: any) => ({
      value: ct.value,
      label: t(ct.value, { ns: "countries" }),
    }))
  }

  if (field === Filters.DeliveryStatus) {
    normalized = filter.map((status: any) => ({
      value: status.value,
      label: t(status.label, { ns: "translation" }),
    }))
  }

  if (field === Filters.Errors) {
    normalized = filter.map((error: any) => ({
      value: error,
      label: t(error, { ns: "errors" }),
    }))
  }

  if (field === Filters.ShowEmpty) {
    normalized = filter.map((hide: any) => ({
      value: hide.value,
      label: t(hide.label, { ns: "translation" }),
    }))
  }

  if (field === Filters.ClientTypes) {
    // hardcoding a translation key so that the i18n parser can detect it
    t("Inconnu")

    normalized = filter.map((type: any) => ({
      value: type,
      label: t(type, { ns: "translation" }),
    }))
  }

  if (
    [
      Filters.Forwarded,
      Filters.Mac,
      Filters.HiddenByAdmin,
      Filters.HiddenByAuditor,
    ].includes(field)
  ) {
    normalized = filter.map((ct: any) => ({
      value: ct.value,
      label: t(ct.label, { ns: "translation" }),
    }))
  }

  return normalized
    .filter(Boolean)
    .sort((a: Option, b: Option) => a.label.localeCompare(b.label, "fr"))
}

export function normalizeSnapshot(snapshot: any, t: TFunction): Snapshot {
  if (snapshot.years) {
    snapshot.years = snapshot.years.map(toOption)
  }

  return snapshot
}

export function filterOutsourcedDepots(snapshot: any): Snapshot {
  snapshot.depots = snapshot.depots.filter(
    (d: EntityDeliverySite) => d.blending_is_outsourced
  )
  return snapshot
}

export function flattenSummary(summary: any): SummaryItem[] {
  const rows = []

  for (const entity in summary) {
    const biocarburants = summary[entity]
    for (const biocarburant in biocarburants) {
      rows.push({
        entity,
        biocarburant,
        ...biocarburants[biocarburant],
      })
    }
  }

  return rows
}

export function normalizeSummary(summary: any): TransactionSummary {
  return {
    in: flattenSummary(summary.in),
    out: flattenSummary(summary.out),
    tx_ids: summary.tx_ids,
    total_volume: summary.total_volume,
    total_remaining_volume: summary.total_remaining_volume,
  }
}

export function flattenGeneralSummary(summary: any): SummaryItem[] {
  const rows = []

  for (const vendor in summary) {
    const clients = summary[vendor]
    for (const client in clients) {
      const biocarburants = clients[client]
      for (const biocarburant in biocarburants) {
        rows.push({
          client,
          vendor,
          biocarburant,
          ...biocarburants[biocarburant],
        })
      }
    }
  }

  return rows
}

export function normalizeGeneralSummary(summary: any): TransactionSummary {
  return {
    transactions: flattenGeneralSummary(summary.transactions),
    tx_ids: summary.tx_ids,
    total_volume: summary.total_volume,
    total_remaining_volume: summary.total_remaining_volume,
  }
}

export function prettyVolume(volume: number) {
  return parseFloat(volume.toFixed(2)).toLocaleString("fr-FR")
}
