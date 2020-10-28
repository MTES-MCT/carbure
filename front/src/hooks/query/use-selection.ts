import { useState } from "react"
import { Transaction } from "../../services/types"

export interface TransactionSelection {
  selected: number[]
  has: (id: number) => boolean
  toggleSelect: (id: number) => void
  toggleSelectAll: (t: boolean) => void
  isAllSelected: () => boolean
  reset: () => void
}

export default function useTransactionSelection(
  transactions?: Transaction[]
): TransactionSelection {
  const [selected, setSelection] = useState<number[]>([])

  const tx = transactions ? transactions.map((t) => t.id) : []

  // if some selected transactions are not on the current list, remove them
  if (selected.some((id) => !tx.includes(id))) {
    setSelection(selected.filter((id) => tx.includes(id)))
  }

  function has(id: number) {
    return selected.includes(id)
  }

  function reset() {
    setSelection([])
  }

  function toggleSelect(id: number) {
    if (has(id)) {
      setSelection(selected.filter((sid) => sid !== id))
    } else {
      setSelection([...selected, id])
    }
  }

  function toggleSelectAll(toggle: boolean) {
    if (toggle) {
      setSelection(tx)
    } else {
      setSelection([])
    }
  }

  function isAllSelected() {
    tx.sort()
    selected.sort()

    return (
      tx.length > 0 &&
      tx.length === selected.length &&
      selected.every((id, i) => tx[i] === id)
    )
  }

  return {
    selected,
    has,
    toggleSelect,
    toggleSelectAll,
    isAllSelected,
    reset,
  }
}
