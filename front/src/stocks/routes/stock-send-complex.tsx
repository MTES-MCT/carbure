import React from "react"
import { Title } from "common/components"

import Modal from "common/components/modal"
import { StockSendComplexForm } from "../components/stock-send-complex-form"
import { EntitySelection } from "carbure/hooks/use-entity"
import useTransactionInSummary from "transactions/hooks/use-transaction-in-summary"

type StockSendComplexProps = {
  entity: EntitySelection
}

export const StockSendComplex = ({ entity }: StockSendComplexProps) => {
  const { request, close } = useTransactionInSummary(entity)

  return (
    <Modal onClose={close}>
      <Title>Envoi complexe</Title>

      <StockSendComplexForm data={request.data} loading={request.loading} />
    </Modal>
  )
}
