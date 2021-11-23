import endOfMonth from "date-fns/endOfMonth"
import { Lot, LotStatus } from "transactions-v2/types"

export function getCurrentDeadline() {
  return endOfMonth(new Date())
}

export function isExpiring(lot: Lot | undefined) {
  const deadline = getCurrentDeadline()
  const deadlinePeriod = deadline.getFullYear() * 100 + deadline.getMonth()
  return deadlinePeriod === lot?.period && UNVALIDATED.includes(lot.lot_status)
}

// lot status that means it is not validated
const UNVALIDATED = [LotStatus.Draft, LotStatus.Pending, LotStatus.Rejected]
