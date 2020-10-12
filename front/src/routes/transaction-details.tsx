import React from "react"

import { Lots } from "../services/types"
import { EntitySelection } from "../hooks/helpers/use-entity"

import useTransactionDetails from "../hooks/use-transaction-details"

import Modal from "../components/system/modal"
import { Button, LoaderOverlay, Title } from "../components/system"
import { Save, Cross } from "../components/system/icons"
import TransactionForm from "../components/transaction-form"
import { ApiState } from "../hooks/helpers/use-api"

type TransactionDetailsProps = {
  entity: EntitySelection
  transactions: ApiState<Lots>
  refresh: () => void
}

const TransactionDetails = ({
  entity,
  transactions,
  refresh,
}: TransactionDetailsProps) => {
  const { form, request, change, submit, close } = useTransactionDetails(
    entity,
    transactions,
    refresh
  )

  return (
    <Modal onClose={close}>
      <Title>Transaction #{form.id ?? "N/A"}</Title>

      <TransactionForm
        transaction={form}
        error={request.error}
        onChange={change}
      >
        <Button
          submit
          name="update"
          icon={Save}
          level="primary"
          onClick={submit}
        >
          Sauvegarder
        </Button>
        <Button icon={Cross} onClick={close}>
          Annuler
        </Button>
      </TransactionForm>

      {transactions.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
