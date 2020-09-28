import React from "react"
import useTransactionDetails from "../hooks/use-transaction-details"

import { Lots } from "../services/types"

type TransactionDetailsProps = {
  transactions: Lots | null
}

const TransactionDetails = ({ transactions }: TransactionDetailsProps) => {
  const transaction = useTransactionDetails(transactions)

  return <span>{JSON.stringify(transaction)}</span>
}

export default TransactionDetails
