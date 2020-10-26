import { useState } from "react"
import { PageSelection } from "../../components/system/pagination"

export interface DeadlineSelection {
  active: boolean
  setDeadline: (v: boolean) => void
}

export default function useDeadlineSelection(pagination: PageSelection) {
  const [active, setDeadlineState] = useState(false)

  function setDeadline(value: boolean) {
    pagination.setPage(0)
    setDeadlineState(value)
  }

  return { active, setDeadline }
}
