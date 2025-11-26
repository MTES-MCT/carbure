import { ElecOperation, ElecOperationType } from "accounting/types"

export const isSendingOperation = (operation: string) =>
  [ElecOperationType.CESSION, ElecOperationType.TENEUR].includes(
    operation as ElecOperationType
  )

export const getOperationEntity = (operation: ElecOperation) =>
  [
    ElecOperationType.TENEUR,
    ElecOperationType.ACQUISITION,
    ElecOperationType.ACQUISITION_FROM_CPO,
  ].includes(operation.type as ElecOperationType)
    ? operation.debited_entity
    : operation.credited_entity

export const getOperationQuantity = (
  operation: ElecOperation,
  formattedQuantity: string
) =>
  isSendingOperation(operation.type)
    ? `-${formattedQuantity}`
    : `+${formattedQuantity}`
