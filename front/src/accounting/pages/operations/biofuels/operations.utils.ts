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

export const isSendingOperation = (quantity: number) => quantity < 0
export const isReceivingOperation = (quantity: number) => quantity > 0

export const getOperationQuantity = (
  operation: Operation,
  formattedQuantity: string
) => {
  if (formattedQuantity.trim().startsWith("-")) {
    return formattedQuantity
  }
  return `+${formattedQuantity}`
}
