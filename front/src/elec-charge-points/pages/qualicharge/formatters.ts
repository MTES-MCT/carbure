import i18next from "i18next"
import { QualichargeValidatedBy } from "./types"

export const formatQualichargeStatus = (status: QualichargeValidatedBy) => {
  switch (status) {
    case QualichargeValidatedBy.BOTH:
      return i18next.t("Validé")
    case QualichargeValidatedBy.DGEC:
      return i18next.t("En attente - Déclarant")
    case QualichargeValidatedBy.CPO:
      return i18next.t("En attente - DGEC")
    case QualichargeValidatedBy.NO_ONE:
      return i18next.t("En attente")
    default:
      return i18next.t("Inconnu")
  }
}
