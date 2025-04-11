import {
  ElecOperationSector,
  ElecOperationsStatus,
  ElecOperationType,
  OperationDebitOrCredit,
  OperationSector,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import i18next from "i18next"

/**
 * Return the i18n key for the sector
 * @param sector the sector sent by the API
 * @returns the i18n key for the sector
 */
export const formatSector = (sector: string) => {
  switch (sector) {
    case OperationSector.ESSENCE:
      return i18next.t("Essence")
    case OperationSector.GAZOLE:
      return i18next.t("Gazole")
    case OperationSector.CARBUR_ACTEUR:
      return i18next.t("Carburéacteur")
    case ElecOperationSector.ELEC:
      return i18next.t("Électricité")
    default:
      return i18next.t("Inconnu")
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
      return i18next.t("Incorporation")
    case OperationType.CESSION:
      return i18next.t("Cession")
    case OperationType.MAC_BIO:
      return i18next.t("Mise à consommation")
    case OperationType.TENEUR:
      return i18next.t("Teneur")
    case OperationType.EXPORTATION:
      return i18next.t("Exportation")
    case OperationType.DEVALUATION:
      return i18next.t("Dévaluation")
    case OperationType.LIVRAISON_DIRECTE:
      return i18next.t("Livraison directe")
    case OperationType.ACQUISITION:
    case ElecOperationType.ACQUISITION_FROM_CPO:
      return i18next.t("Acquisition")
    default:
      return i18next.t("Inconnu")
  }
}

export const formatOperationStatus = (
  status: OperationsStatus | ElecOperationsStatus
) => {
  switch (status) {
    case OperationsStatus.ACCEPTED:
      return i18next.t("Accepté")
    case OperationsStatus.CANCELED:
      return i18next.t("Annulé")
    case OperationsStatus.PENDING:
      return i18next.t("En attente")
    case OperationsStatus.REJECTED:
      return i18next.t("Rejeté")
    case OperationsStatus.DECLARED:
      return i18next.t("Déclaré")
    case OperationsStatus.CORRECTED:
      return i18next.t("Corrigé")
    case OperationsStatus.VALIDATED:
      return i18next.t("Validé")
    default:
      return i18next.t("Inconnu")
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
