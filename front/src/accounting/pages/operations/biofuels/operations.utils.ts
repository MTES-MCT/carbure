import { Operation, OperationDebitOrCredit } from "accounting/types"

export const formatOperationCreditOrDebit = (type: string) => {
  switch (type) {
    case OperationDebitOrCredit.CREDIT:
      return "Crédit"
    case OperationDebitOrCredit.DEBIT:
      return "Débit"
    default:
      return "Inconnu"
  }
}

export const isOperationDebit = (operation: Operation, entityId: number) => {
  return operation.debited_entity && operation.debited_entity.id === entityId
}

export const getOperationEntity = (operation: Operation, entityId: number) => {
  if (operation.credited_entity && operation.credited_entity.id === entityId) {
    return operation.debited_entity
  }
  return operation.credited_entity
}

export const getOperationQuantity = (
  operation: Operation,
  formattedQuantity: string,
  entityId: number
) =>
  isOperationDebit(operation, entityId)
    ? `-${formattedQuantity}`
    : `+${formattedQuantity}`
