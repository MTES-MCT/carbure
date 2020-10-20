import { useParams } from "react-router-dom"

import { PageSelection } from "../../components/system/pagination"
import { LotStatus } from "../../services/types"

import { useRelativePush } from "../../components/relative-route"
import { InvalidSelection } from "./use-invalid"

export interface StatusSelection {
  active: LotStatus
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
export default function useStatusSelection(
  pagination: PageSelection,
  invalid: InvalidSelection
): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

  const active = params.status

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    invalid.setInvalid(false)
    push(`../${status}`)
  }

  return { active, setActive }
}
