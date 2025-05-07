import {
  Operation,
  OperationDebitOrCredit,
  OperationType,
} from "accounting/types"

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

export const isOperationDebit = (operation: string) =>
  [
    OperationType.CESSION,
    OperationType.TENEUR,
    OperationType.EXPORTATION,
    OperationType.DEVALUATION,
  ].includes(operation as OperationType)

export const getOperationQuantity = (
  operation: Operation,
  formattedQuantity: string
) =>
  isOperationDebit(operation.type)
    ? `-${formattedQuantity}`
    : `+${formattedQuantity}`
