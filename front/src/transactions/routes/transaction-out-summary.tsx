import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"

import { Title } from "common/system"
import Modal from "common/system/modal"
import useTransactionOutSummary from "../hooks/use-transaction-out-summary"
import TransactionOutSummaryForm from "../components/transaction-out-summary-form"

type TransactionOutSummaryProps = {
  entity: EntitySelection
}

const TransactionOutSummary = ({ entity }: TransactionOutSummaryProps) => {
  const { request, close } = useTransactionOutSummary(entity)

  return (
    <Modal onClose={close}>
      <Title>Bilan des sorties</Title>

      <TransactionOutSummaryForm
        data={request.data}
        loading={request.loading}
      />
    </Modal>
  )
}

export default TransactionOutSummary
