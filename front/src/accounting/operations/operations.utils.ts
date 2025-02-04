import {
  Operation,
  OperationDebitOrCredit,
  OperationSector,
  OperationsStatus,
  OperationType,
} from "./types"
import { formatNumber } from "common/utils/formatters"

/**
 * Return the i18n key for the sector
 * @param sector the sector sent by the API
 * @returns the i18n key for the sector
 */
export const formatSector = (sector: string) => {
  switch (sector) {
    case OperationSector.ESSENCE:
      return "Essence"
    case OperationSector.DIESEL:
      return "Gazole"
    case OperationSector.SAF:
      return "Carburéacteur"
    default:
      return "Inconnu"
  }
}

/**
 * Return the i18n key for the operation type
 * @param type the operation type sent by the API
 * @returns the i18n key for the operation type
 */
export const formatOperationType = (type: string) => {
  switch (type) {
    case OperationType.INCORPORATION:
      return "Incorporation"
    case OperationType.CESSION:
      return "Cession"
    case OperationType.MAC_BIO:
      return "Mise à consommation"
    case OperationType.TENEUR:
      return "Teneur"
    case OperationType.EXPORTATION:
      return "Exportation"
    case OperationType.DEVALUATION:
      return "Dévaluation"
    case OperationType.LIVRAISON_DIRECTE:
      return "Livraison directe"
    case OperationType.ACQUISITION:
      return "Acquisition"
    default:
      return "Inconnu"
  }
}

export const formatOperationStatus = (status: OperationsStatus) => {
  switch (status) {
    case OperationsStatus.ACCEPTED:
      return "Validé"
    case OperationsStatus.CANCELED:
      return "Annulé"
    case OperationsStatus.PENDING:
      return "En attente"
    case OperationsStatus.REJECTED:
      return "Rejeté"
    default:
      return "Inconnu"
  }
}

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

export const getOperationVolume = (operation: Operation) =>
  isOperationDebit(operation.type)
    ? `-${formatNumber(operation.volume)}`
    : `+${formatNumber(operation.volume)}`
