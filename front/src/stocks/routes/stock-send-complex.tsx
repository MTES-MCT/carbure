import React from "react"
import { Title } from "common/components"

import Modal from "common/components/modal"
import { StockSendComplexForm } from "../components/send-complex-form"
import { EntitySelection } from "carbure/hooks/use-entity"
import useStockSendComplex from "stocks/hooks/use-send-complex"

type StockSendComplexProps = {
  entity: EntitySelection
}

const StockSendComplex = ({ entity }: StockSendComplexProps) => {
  const { request, close } = useStockSendComplex(entity)

  return (
    <Modal onClose={close}>
      <Title>Envoi complexe</Title>

      <StockSendComplexForm data={request.data} loading={request.loading} />
    </Modal>
  )
}

export default StockSendComplex
