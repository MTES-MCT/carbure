import React from "react"
import { Redirect } from "react-router-dom"

import { Lots } from "../services/types"

import useTransactionDetails from "../hooks/use-transaction-details"

type TransactionDetailsProps = {
  transactions: Lots | null
}

const TransactionDetails = ({ transactions }: TransactionDetailsProps) => {
  const transaction = useTransactionDetails(transactions)

  if (transaction === null) {
    return <Redirect to="/transactions" />
  }

  return <span>{JSON.stringify(transaction)}</span>
}

export default TransactionDetails
