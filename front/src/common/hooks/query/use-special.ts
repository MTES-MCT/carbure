import { useState } from "react"
import { PageSelection } from "../../components/pagination"

export interface SpecialSelection {
  invalid: boolean
  deadline: boolean
  setDeadline: (v: boolean) => void
  setInvalid: (v: boolean) => void
  reset: () => void
}

export default function useSpecialSelection(
  pagination: PageSelection
): SpecialSelection {
  const [invalid, setInvalidState] = useState(false)
  const [deadline, setDeadlineState] = useState(false)

  function setDeadline(value: boolean) {
    pagination.setPage(0)
    setInvalidState(false)
    setDeadlineState(value)
  }

  function setInvalid(value: boolean) {
    pagination.setPage(0)
    setDeadlineState(false)
    setInvalidState(value)
  }

  function reset() {
    setInvalidState(false)
    setDeadlineState(false)
  }

  return { invalid, deadline, setDeadline, setInvalid, reset }
}
