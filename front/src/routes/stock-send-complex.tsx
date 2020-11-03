import React from "react"
import { Title } from "../components/system"

import Modal from "../components/system/modal"
import { StockSendComplexForm } from "../components/stock-send-complex-form"
import { EntitySelection } from "../hooks/helpers/use-entity"
import useTransactionInSummary from "../hooks/use-transaction-in-summary"

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
