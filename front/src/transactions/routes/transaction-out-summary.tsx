import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"

import { Title } from "common/components"
import Modal from "common/components/modal"
import TransactionOutSummaryTable from "../components/summary-out"
import useTransactionOutSummary from "../hooks/use-transaction-out-summary"
import { LotStatus } from "common/types"

type TransactionOutSummaryProps = {
  entity: EntitySelection
  lot_status: LotStatus
  period: string
  delivery_status: string[]
  stock: boolean
}

const TransactionOutSummary = ({ entity, lot_status, period, delivery_status, stock }: TransactionOutSummaryProps) => {
  const { request, close } = useTransactionOutSummary(entity, lot_status, period, delivery_status, stock)

  return (
    <Modal onClose={close}>
      <Title>Bilan des sorties</Title>

      <TransactionOutSummaryTable
        data={request.data}
        loading={request.loading}
      />
    </Modal>
  )
}

export default TransactionOutSummary
