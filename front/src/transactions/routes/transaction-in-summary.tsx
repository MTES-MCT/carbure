import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"

import { Title } from "common/components"
import Modal from "common/components/modal"
import TransactionInSummaryForm from "../components/transaction-in-summary-form"
import useTransactionInSummary from "../hooks/use-transaction-in-summary"

type TransactionInSummaryProps = {
  entity: EntitySelection
}

const TransactionInSummary = ({ entity }: TransactionInSummaryProps) => {
  const { request, close } = useTransactionInSummary(entity)

  return (
    <Modal onClose={close}>
      <Title>Bilan des entrées</Title>

      <TransactionInSummaryForm data={request.data} loading={request.loading} />
    </Modal>
  )
}

export default TransactionInSummary
