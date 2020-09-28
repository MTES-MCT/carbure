import React from "react"
import { Redirect, useHistory } from "react-router-dom"

import { Lots } from "../services/types"

import useTransactionDetails from "../hooks/use-transaction-details"

import { Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionForm from "../components/transaction-form"
import { Save, Cross } from "../components/system/icons"

type TransactionDetailsProps = {
  transactions: Lots | null
}

const TransactionDetails = ({ transactions }: TransactionDetailsProps) => {
  const history = useHistory()
  const [transaction, change] = useTransactionDetails(transactions)

  if (transaction === null) {
    return <Redirect to="/transactions" />
  }

  function close() {
    history.push("/transactions")
  }

  return (
    <Modal onClose={close}>
      <Title>Transaction #{transaction.id}</Title>
      <TransactionForm transaction={transaction} onChange={change} />

      <Modal.Buttons>
        <Button type="primary">
          <Save /> Sauvegarder
        </Button>
        <Button onClick={close}>
          <Cross /> Annuler
        </Button>
      </Modal.Buttons>
    </Modal>
  )
}

export default TransactionDetails
