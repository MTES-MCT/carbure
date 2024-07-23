import endOfMonth from "date-fns/endOfMonth"
import subMonths from "date-fns/subMonths"
import { Lot, LotStatus } from "transactions/types"

export function getCurrentDeadline() {
	return endOfMonth(new Date())
}

export function isExpiring(lot: Lot | undefined) {
	const deadline = getCurrentDeadline()
	const monthBefore = subMonths(deadline, 1)
	const deadlinePeriod =
		monthBefore.getFullYear() * 100 + (monthBefore.getMonth() + 1)
	return deadlinePeriod === lot?.period && UNVALIDATED.includes(lot.lot_status)
}

// lot status that means it is not validated
const UNVALIDATED = [LotStatus.Draft, LotStatus.Pending, LotStatus.Rejected]
