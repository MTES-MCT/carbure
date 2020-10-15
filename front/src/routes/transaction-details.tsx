import React from "react"

import { Lots } from "../services/types"
import { EntitySelection } from "../hooks/helpers/use-entity"

import useTransactionDetails from "../hooks/use-transaction-details"

import Modal from "../components/system/modal"
import { AsyncButton, Button, LoaderOverlay, Title } from "../components/system"
import { Save, Cross } from "../components/system/icons"
import TransactionForm from "../components/transaction-form"
import { ApiState } from "../hooks/helpers/use-api"

function getFieldErrors(transactions: Lots | null, id: number) {
  if (transactions === null) return {}

  const fieldErrors: { [k: string]: string } = {}

  const lotsErrors = transactions.lots_errors[id] ?? []
  const txErrors = transactions.tx_errors[id] ?? []

  lotsErrors.forEach(({ field, error }) => {
    fieldErrors[field] = fieldErrors[field]
      ? `${fieldErrors[field]}, ${error}`
      : error
  })

  txErrors.forEach(({ field, error }) => {
    fieldErrors[field] = fieldErrors[field]
      ? `${fieldErrors[field]}, ${error}`
      : error
  })

  return fieldErrors
}

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
        fieldErrors={getFieldErrors(transactions.data, form.id)}
      >
        <AsyncButton
          submit
          icon={Save}
          level="primary"
          loading={request.loading}
          onClick={submit}
        >
          Sauvegarder
        </AsyncButton>
        <Button icon={Cross} onClick={close}>
          Annuler
        </Button>
      </TransactionForm>

      {transactions.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
