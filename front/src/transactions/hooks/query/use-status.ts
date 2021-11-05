import { useParams, useNavigate } from "react-router-dom"

import { PageSelection } from "../../../common/components/pagination"
import { SpecialSelection } from "./use-special"
import { LotStatus } from "../../../common/types"


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
  const navigate = useNavigate()
  const params = useParams<"status">()

  const active = params.status as LotStatus ?? LotStatus.Weird

  function is(status: LotStatus) {
    return active === status
  }

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    special.reset()
    navigate(`../${status}`)
  }

  return { active, is, setActive }
}

// manage currently selected transaction status
export function useStockStatusSelection(
  pagination: PageSelection
): StatusSelection {
  const navigate = useNavigate()
  const params = useParams<"status">()

  const active: LotStatus = params.status as LotStatus ?? LotStatus.Draft

  function is(status: LotStatus) {
    return active === status
  }

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    navigate(`../${status}`)
  }

  return { active, is, setActive }
}
