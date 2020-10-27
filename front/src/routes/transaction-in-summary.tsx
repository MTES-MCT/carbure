import React from "react"
import { Title } from "../components/system"

import Modal from "../components/system/modal"
import TransactionInSummaryForm from "../components/transaction-in-summary-form"
import { EntitySelection } from "../hooks/helpers/use-entity"
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
