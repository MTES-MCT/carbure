import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"

import { Title } from "common/components"
import Modal from "common/components/modal"
import TransactionInSummaryTable from "../components/summary-in"
import useTransactionInSummary from "../hooks/use-transaction-in-summary"
import { LotStatus } from "common/types"

type TransactionInSummaryProps = {
  entity: EntitySelection
  lot_status: LotStatus
  period: string | null
  delivery_status: string[]
}

const TransactionInSummary = ({ entity, lot_status, period, delivery_status }: TransactionInSummaryProps) => {
  const { request, close } = useTransactionInSummary(entity, lot_status, period, delivery_status)

  return (
    <Modal onClose={close}>
      <Title>Bilan des entrées</Title>

      <TransactionInSummaryTable
        data={request.data}
        loading={request.loading}
      />
    </Modal>
  )
}

export default TransactionInSummary
