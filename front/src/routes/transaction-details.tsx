import React from "react"

import { Lots, LotStatus } from "../services/types"
import { EntitySelection } from "../hooks/helpers/use-entity"

import useTransactionDetails from "../hooks/use-transaction-details"

import Modal from "../components/system/modal"
import { AsyncButton, LoaderOverlay, Title } from "../components/system"
import { Save } from "../components/system/icons"
import TransactionForm from "../components/transaction-form"
import { ApiState } from "../hooks/helpers/use-api"

function canSave(status: LotStatus | null) {
  return (
    (status !== null && status === LotStatus.Draft) ||
    status === LotStatus.Validated
  )
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
  const {
    form,
    request,
    status,
    fieldErrors,
    change,
    submit,
    close,
  } = useTransactionDetails(entity, transactions, refresh)

  return (
    <Modal onClose={close}>
      <Title>Transaction #{form.id ?? "N/A"}</Title>

      <TransactionForm
        readOnly={!canSave(status)}
        transaction={form}
        error={request.error}
        fieldErrors={fieldErrors}
        onChange={change}
        onClose={close}
      >
        {canSave(status) && (
          <AsyncButton
            submit
            icon={Save}
            level="primary"
            loading={request.loading}
            onClick={submit}
          >
            Sauvegarder
          </AsyncButton>
        )}
      </TransactionForm>

      {transactions.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
