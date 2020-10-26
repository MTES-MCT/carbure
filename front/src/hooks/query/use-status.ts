import { useParams } from "react-router-dom"

import { PageSelection } from "../../components/system/pagination"
import { LotStatus } from "../../services/types"
import { InvalidSelection } from "./use-invalid"
import { DeadlineSelection } from "./use-deadline"

import { useRelativePush } from "../../components/relative-route"

export interface StatusSelection {
  active: LotStatus
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

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    invalid.setInvalid(false)
    deadline.setDeadline(false)
    push(`../${status}`)
  }

  return { active, setActive }
}
