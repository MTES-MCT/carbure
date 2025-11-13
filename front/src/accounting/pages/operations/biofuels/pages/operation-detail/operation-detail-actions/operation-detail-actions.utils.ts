import { OperationType } from "accounting/types"
import i18next from "i18next"

export const getOperationValidationButtonText = (
  operationType: OperationType
) => {
  switch (operationType) {
    case OperationType.TRANSFERT:
      return i18next.t("Transférer")
    case OperationType.EXPORTATION:
      return i18next.t("Exporter")
    case OperationType.EXPEDITION:
      return i18next.t("Expédier")
    default:
      return i18next.t("Valider")
  }
}
