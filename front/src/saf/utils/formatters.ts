import { t } from "i18next"
import { ConsumptionType, EtsStatus } from "saf/types"

// Returns only the key of translation to be reactive during changing language
export const formatConsumptionType = (consumptionType: ConsumptionType) => {
  switch (consumptionType) {
    case ConsumptionType.MAC:
      return t("Mise à consommation")
    case ConsumptionType.MAC_DECLASSEMENT:
      return t("Déclassement")
  }
  return ""
}

export const formatEtsStatus = (etsStatus: EtsStatus) => {
  switch (etsStatus) {
    case EtsStatus.ETS_VALUATION:
      return t("Valorisation ETS")
    case EtsStatus.OUTSIDE_ETS:
      return t("Hors ETS (volontaire)")
    case EtsStatus.NOT_CONCERNED:
      return t("Non concerné")
  }
}
