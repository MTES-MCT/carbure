import { useParams } from "react-router-dom"

import { PageSelection } from "../../components/system/pagination"
import { LotStatus } from "../../services/types"
import { InvalidSelection } from "./use-invalid"
import { DeadlineSelection } from "./use-deadline"

import { useRelativePush } from "../../components/relative-route"

export interface StatusSelection {
  active: LotStatus
  is: (s: LotStatus) => boolean
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
export default function useStatusSelection(
  pagination: PageSelection,
  invalid: InvalidSelection,
  deadline: DeadlineSelection
): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

  const active = params.status

  function is(status: LotStatus) {
    return active === status
  }

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    invalid.setInvalid(false)
    deadline.setDeadline(false)
    push(`../${status}`)
  }

  return { active, is, setActive }
}

// manage currently selected transaction status
export function useStockStatusSelection(
  pagination: PageSelection,
): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

  console.log(`Stock status: ${params.status}`)
  if (params.status === null || params.status === undefined) {
    params.status = LotStatus.Draft
  }
  const active = params.status



  function is(status: LotStatus) {
    return active === status
  }

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    push(`../${status}`)
  }

  return { active, is, setActive }
}
