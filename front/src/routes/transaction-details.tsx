import React from "react"
import { Redirect } from "react-router-dom"

import { Lots } from "../services/types"

import useTransactionDetails from "../hooks/use-transaction-details"

import { Box, Title } from "../components/system"
import TransactionForm from "../components/transaction-form"

type TransactionDetailsProps = {
  transactions: Lots | null
}

const TransactionDetails = ({ transactions }: TransactionDetailsProps) => {
  const [transaction, change] = useTransactionDetails(transactions)

  if (transaction === null) {
    return <Redirect to="/transactions" />
  }

  console.log(transaction)

  return (
    <Box>
      <Title>Transaction #{transaction.id}</Title>
      <TransactionForm transaction={transaction} onChange={change} />
    </Box>
  )
}

export default TransactionDetails
