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

export const getOperationQuantity = (
  operation: Operation,
  formattedQuantity: string,
  entityId: number
) =>
  isOperationDebit(operation, entityId)
    ? `-${formattedQuantity}`
    : `+${formattedQuantity}`
