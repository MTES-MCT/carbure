import { useParams } from "react-router-dom"
import { Lots } from "../services/types"

export default function useTransactionDetails(transactions: Lots | null) {
  const params: { id: string } = useParams()
  const transactionID = parseInt(params.id, 10)

  if (transactions === null) {
    return null
  }

  // find the relevant lot
  // @TODO would be nice to be able to fetch details for only one lot
  const transaction = transactions.lots.find(
    (lot) => lot.lot.id === transactionID
  )

  return transaction
}
