import { useParams } from "react-router-dom"

import { PageSelection } from "../../components/system/pagination"
import { SpecialSelection } from "./use-special"
import { LotStatus } from "../../services/types"

import { useRelativePush } from "../../components/relative-route"

export interface StatusSelection {
  active: LotStatus
  is: (s: LotStatus) => boolean
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
export default function useStatusSelection(
  pagination: PageSelection,
  special: SpecialSelection
): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

  const active = params.status

  function is(status: LotStatus) {
    return active === status
  }

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    special.reset()
    push(`../${status}`)
  }

  return { active, is, setActive }
}

// manage currently selected transaction status
export function useStockStatusSelection(
  pagination: PageSelection
): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

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
