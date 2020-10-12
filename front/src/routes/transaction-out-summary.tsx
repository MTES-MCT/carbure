import React from "react"
import { Redirect } from "react-router-dom"

import { AsyncButton, Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionOutSummaryForm from "../components/transaction-out-summary-form"
import { EntitySelection } from "../hooks/helpers/use-entity"
import useTransactionOutSummary from "../hooks/use-transaction-out-summary"

type TransactionOutSummaryProps = {
  entity: EntitySelection
}

const TransactionOutSummary = ({ entity }: TransactionOutSummaryProps) => {
  const { form, request, change, close } = useTransactionOutSummary(entity)

  if (entity === null) {
    return <Redirect to="/transactions" />
  }

  return (
    <Modal onClose={close}>
      <Title>Bilan des sorties</Title>

      <TransactionOutSummaryForm data={form!} onChange={change} />
    </Modal>
  )
}

export default TransactionOutSummary
