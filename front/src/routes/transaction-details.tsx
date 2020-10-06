import React from "react"
import { Redirect } from "react-router-dom"

import { Lots } from "../services/types"
import { EntitySelection } from "../hooks/use-app"

import useTransactionDetails from "../hooks/use-transaction-details"

import Modal from "../components/system/modal"
import { Button, Title } from "../components/system"
import { Save, Cross } from "../components/system/icons"
import TransactionForm from "../components/transaction-form"

type TransactionDetailsProps = {
  entity: EntitySelection
  transactions: Lots | null
}

const TransactionDetails = ({
  entity,
  transactions,
}: TransactionDetailsProps) => {
  const { form, request, change, submit, close } = useTransactionDetails(
    entity,
    transactions
  )

  if (form === null) {
    return <Redirect to="/transactions" />
  }

  return (
    <Modal onClose={close}>
      <Title>Transaction #{form.id}</Title>

      <TransactionForm
        transaction={form}
        error={request.error}
        onChange={change}
      >
        <Button
          submit
          name="update"
          icon={Save}
          kind="primary"
          onClick={submit}
        >
          Sauvegarder
        </Button>
        <Button icon={Cross} onClick={close}>
          Annuler
        </Button>
      </TransactionForm>
    </Modal>
  )
}

export default TransactionDetails
