import { useParams } from "react-router"
import { useRelativePush } from "common/components/relative-route"

export default function useNavigate(transactions: number[]) {
  const push = useRelativePush()
  const params: { id: string } = useParams()
  const current = parseInt(params.id)

  const index = transactions.indexOf(current)
  const total = transactions.length

  const hasPrev = index > 0
  const hasNext = 0 <= index && index < transactions.length - 1

  function prev() {
    if (hasPrev) {
      push(`../${transactions[index - 1]}`)
    }
  }

  function next() {
    if (hasNext) {
      push(`../${transactions[index + 1]}`)
    }
  }

  return {
    index,
    total,
    hasPrev,
    hasNext,
    prev,
    next,
  }
}
