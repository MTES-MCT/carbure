import React from "react"
import { Title } from "../components/system"

import Modal from "../components/system/modal"
import TransactionInSummaryForm from "../components/transaction-in-summary-form"
import { EntitySelection } from "../hooks/helpers/use-entity"
import useTransactionInSummary from "../hooks/use-transaction-in-summary"

type StockInSummaryProps = {
  entity: EntitySelection
}

export const StockInSummary = ({ entity }: StockInSummaryProps) => {
  const { request, close } = useTransactionInSummary(entity)

  return (
    <Modal onClose={close}>
      <Title>Bilan des entrées</Title>

      <TransactionInSummaryForm data={request.data} loading={request.loading} />
    </Modal>
  )
}

