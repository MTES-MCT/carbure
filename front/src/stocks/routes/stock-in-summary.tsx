import React from "react"
import { Title } from "../../common/system"

import Modal from "../../common/system/modal"
import TransactionInSummaryForm from "../../transactions/components/transaction-in-summary-form"
import { EntitySelection } from "../../common/hooks/helpers/use-entity"
import useTransactionInSummary from "../../transactions/hooks/use-transaction-in-summary"

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
