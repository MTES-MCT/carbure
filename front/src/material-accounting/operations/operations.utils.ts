import { OperationType } from "./types"

/**
 * Return the i18n key for the sector
 * @param sector the sector sent by the API
 * @returns the i18n key for the sector
 */
export const formatSector = (sector: string) => {
  switch (sector) {
    case "ESSENCE":
      return "Essence"
    case "DIESEL":
      return "Gazole"
    case "AVIATION":
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
