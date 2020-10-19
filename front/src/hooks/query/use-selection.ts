import { useState } from "react"
import { Transaction } from "../../services/types"

export interface TransactionSelection {
  selected: number[]
  has: (id: number) => boolean
  selectOne: (id: number) => void
  selectMany: React.Dispatch<React.SetStateAction<number[]>>
  reset: () => void
}

export default function useTransactionSelection(
  transactions?: Transaction[]
): TransactionSelection {
  const [selected, selectMany] = useState<number[]>([])

  const tx = transactions ? transactions.map((t) => t.id) : []

  // if some selected transactions are not on the current list, remove them
  if (selected.some((id) => !tx.includes(id))) {
    selectMany(selected.filter((id) => tx.includes(id)))
  }

  function has(id: number) {
    return selected.includes(id)
  }

  function reset() {
    selectMany([])
  }

  function selectOne(id: number) {
    if (has(id)) {
      selectMany(selected.filter((sid) => sid !== id))
    } else {
      selectMany([...selected, id])
    }
  }

  return { selected, has, selectOne, selectMany, reset }
}
