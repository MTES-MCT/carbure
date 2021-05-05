import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

import {
  Filters,
  Snapshot,
  Transaction,
  LotStatus,
  SummaryItem,
  Errors,
} from "common/types"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { Option } from "common/components/select"

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
  errors: Record<number, Errors>
): boolean {
  if (!tx || !errors[tx.id]) return false

  return (
    errors[tx.id].validation_errors?.some(
      (e) => e.is_warning && !e.is_blocking
    ) ?? false
  )
}

export function hasErrors(
  tx: Transaction,
  errors: Record<number, Errors>
): boolean {
  if (!tx || !errors[tx.id]) return false

  const hasTxErrors = Boolean(errors[tx.id].tx_errors)
  const hasLotErrors = Boolean(errors[tx.id].lots_errors)
  const hasBlockingErrors = errors[tx.id].validation_errors?.some((e) => e.is_blocking) ?? false // prettier-ignore

  return hasTxErrors || hasLotErrors || hasBlockingErrors
}

// extract the status name from the lot details
export function getStatus(
  transaction: Transaction,
  entityID: number
): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  const isAuthor = transaction.lot.added_by?.id === entityID
  const isVendor = transaction.carbure_vendor?.id === entityID
  const isClient = transaction.carbure_client?.id === entityID

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (delivery === "A") {
      return LotStatus.Accepted
    }
    // OPERATEUR
    else if (isClient && ["N", "AA", "AC"].includes(delivery)) {
      return LotStatus.Inbox
    }
    // PRODUCTEUR
    else if (isVendor || isAuthor) {
      if (["N", "AA"].includes(delivery)) {
        return LotStatus.Validated
      } else if (["AC", "R"].includes(delivery)) {
        return LotStatus.ToFix
      }
    }
  }

  return LotStatus.Weird
}

// give the same type to all filters in order to render them easily
export function normalizeFilters(snapshot: any): Snapshot {
  Object.values(Filters).forEach((key) => {
    const filter = snapshot.filters[key]

    if (filter && typeof filter[0] === "string") {
      const set = new Set<string>(filter)
      snapshot.filters[key] = Array.from(set).map(toOption)
    }

    if (key in snapshot.filters) {
      snapshot.filters[key].sort((a: Option, b: Option) =>
        a.label.localeCompare(b.label, "fr")
      )
    }
  })

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

export function prettyVolume(volume: number) {
  return parseFloat(volume.toFixed(2)).toLocaleString("fr-FR")
}
