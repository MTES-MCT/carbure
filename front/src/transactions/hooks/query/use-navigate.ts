import { useParams } from "react-router"
import { useRelativePush } from "common/components/relative-route"
import { useCallback, useEffect } from "react"

export default function useNavigate(transactions: number[]) {
  const push = useRelativePush()
  const params: { id: string } = useParams()
  const current = parseInt(params.id)

  const index = transactions.indexOf(current)
  const total = transactions.length

  const isOut = index < 0
  const hasPrev = index > 0
  const hasNext = index < transactions.length - 1

  const prev = useCallback(() => {
    if (hasPrev) {
      push(`../${transactions[index - 1]}`)
    }
  }, [transactions, hasPrev, index, push])

  const next = useCallback(() => {
    if (isOut) {
      push(`../${transactions[0]}`)
    } else if (hasNext) {
      push(`../${transactions[index + 1]}`)
    }
  }, [transactions, hasNext, isOut, index, push])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.target as Element)?.matches("input")) {
        return
      }

      if (e.key === "ArrowLeft") {
        prev()
      } else if (e.key === "ArrowRight") {
        next()
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [prev, next])

  return {
    index,
    total,
    isOut,
    hasPrev,
    hasNext,
    prev,
    next,
  }
}
