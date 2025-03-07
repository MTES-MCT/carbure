import { OperationType } from "accounting/types"
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

export const isOperationDebit = (operation: string) =>
  [
    OperationType.CESSION,
    OperationType.TENEUR,
    OperationType.EXPORTATION,
    OperationType.DEVALUATION,
  ].includes(operation as OperationType)

export const getOperationEntity = (operation: Operation) =>
  [
    OperationType.TENEUR,
    OperationType.EXPORTATION,
    OperationType.DEVALUATION,
    OperationType.ACQUISITION,
  ].includes(operation.type as OperationType)
    ? operation.debited_entity
    : operation.credited_entity

export const getOperationQuantity = (
  operation: Operation,
  formattedQuantity: string
) =>
  isOperationDebit(operation.type)
    ? `-${formattedQuantity}`
    : `+${formattedQuantity}`
