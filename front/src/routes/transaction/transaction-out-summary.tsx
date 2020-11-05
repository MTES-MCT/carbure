import React from "react"

import { Title } from "../../components/system"
import Modal from "../../components/system/modal"
import TransactionOutSummaryForm from "../../components/transaction/transaction-out-summary-form"
import { EntitySelection } from "../../hooks/helpers/use-entity"
import useTransactionOutSummary from "../../hooks/use-transaction-out-summary"

type TransactionOutSummaryProps = {
  entity: EntitySelection
}

const TransactionOutSummary = ({ entity }: TransactionOutSummaryProps) => {
  const { request, close } = useTransactionOutSummary(entity)

  return (
    <Modal onClose={close}>
      <Title>Bilan des sorties</Title>

      <TransactionOutSummaryForm data={request.data} loading={request.loading} />
    </Modal>
  )
}

export default TransactionOutSummary
