import {
  FRACTION_DIGITS_GJ,
  FRACTION_DIGITS_LITERS,
  FRACTION_DIGITS_TCO2,
} from "accounting/config"
import {
  DevaluationType,
  ElecOperationSector,
  ElecOperationsStatus,
  ElecOperationType,
  OperationDebitOrCredit,
  OperationSector,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import { apiTypes } from "common/services/api-fetch.types"
import { ExtendedUnitType, Unit } from "common/types"
import {
  formatNumber,
  FormatNumberOptions,
  formatUnit,
} from "common/utils/formatters"
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
    case OperationSector.GPL:
      return i18next.t("GPL")
    case OperationSector.MARITIME:
      return i18next.t("Maritime")
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
export const formatOperationType = (type: string, year?: number) => {
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
    case OperationType.EXPEDITION:
      return i18next.t("Expédition")
    case OperationType.DEVALUATION:
      return i18next.t("Dévalorisation")
    case OperationType.LIVRAISON_DIRECTE:
      return i18next.t("Livraison directe")
    case OperationType.ACQUISITION:
      return i18next.t("Acquisition")
    case OperationType.TRANSFERT:
      return i18next.t("Transfert de droits")
    case ElecOperationType.ACQUISITION_FROM_CPO:
      return i18next.t("Acquisition (aménageurs)")
    case OperationType.EXPIRATION:
      return i18next.t("Expiration")
    case OperationType.REPORT:
      return i18next.t("Report Tiruert 2026")
    case OperationType.YEARLY_BALANCE:
      return year ? i18next.t("Reliquat " + (year! - 1)) : i18next.t("Reliquat")
    default:
      return i18next.t("Inconnu")
  }
}

/**
 * Return the i18n key for the devaluation type
 * @param type the devaluation type sent by the API
 * @returns the i18n key for the devaluation type
 */
export const formatDevaluationType = (type: string) => {
  switch (type) {
    case DevaluationType.LOSS:
      return i18next.t("Perte")
    case DevaluationType.DOWNGRADING:
      return i18next.t("Déclassement")
    case DevaluationType.OTHER:
      return i18next.t("Autre")
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
    case OperationsStatus.DRAFT:
      return i18next.t("Brouillon")
    case OperationsStatus.AUTO:
      return i18next.t("Auto")
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

export const formatObjectiveCategory = (category: string) => {
  switch (category) {
    default:
      return category
  }
}

export const formatOperation = (
  operation: apiTypes["OperationList"] | apiTypes["Operation"]
) => ({
  quantity_renewable:
    operation.volume * (operation.renewable_energy_share ?? 1),
})

export const formatAccountingUnit = (value: number, unit: ExtendedUnitType) =>
  formatUnit(value, unit, {
    fractionDigits:
      unit === Unit.l ? FRACTION_DIGITS_LITERS : FRACTION_DIGITS_GJ,
  })

export const formatEnergyNumber = (
  value: number,
  options?: FormatNumberOptions
) =>
  formatNumber(value, {
    fractionDigits: FRACTION_DIGITS_GJ,
    ...options,
  })

export const formatTCO2Number = (
  value: number,
  options?: FormatNumberOptions
) =>
  formatNumber(value, {
    fractionDigits: FRACTION_DIGITS_TCO2,
    ...options,
  })
