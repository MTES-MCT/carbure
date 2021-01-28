import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

import {
  Filters,
  Snapshot,
  Transaction,
  LotStatus,
  SummaryItem,
} from "common/types"

export function toOption(value: string) {
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

// extract the status name from the lot details
export function getStatus(transaction: Transaction, entity: number): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  const isVendor = transaction.carbure_vendor?.id === entity
  const isClient = transaction.carbure_client?.id === entity

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
    else if (isVendor) {
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
      snapshot.filters[key] = filter.map(toOption)
    }
  })

  snapshot.years = snapshot.years.map(toOption)

  return snapshot
}

export function flattenSummary(summary: any): SummaryItem[] {
  const rows = []

  for (const entity in summary) {
    const deliveries = summary[entity]
    for (const depot in deliveries) {
      const biocarburants = deliveries[depot]
      for (const biocarburant in biocarburants) {
        rows.push({
          entity,
          depot,
          biocarburant,
          ...biocarburants[biocarburant],
        })
      }
    }
  }

  return rows
}
