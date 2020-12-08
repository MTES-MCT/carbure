import { useParams } from "react-router-dom"

import { PageSelection } from "../../../common/components/pagination"
import { SpecialSelection } from "./use-special"
import { LotStatus } from "../../../common/types"

import { useRelativePush } from "../../../common/components/relative-route"

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
