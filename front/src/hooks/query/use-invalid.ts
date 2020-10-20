import { useState } from "react"
import { PageSelection } from "../../components/system/pagination"

export interface InvalidSelection {
  active: boolean
  setInvalid: (v: boolean) => void
}

export default function useInvalidSelection(pagination: PageSelection) {
  const [active, setInvalidState] = useState(false)

  function setInvalid(value: boolean) {
    pagination.setPage(0)
    setInvalidState(value)
  }

  return { active, setInvalid }
}
