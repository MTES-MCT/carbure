import { ConsumptionType } from "saf/types"

// Returns only the key of translation to be reactive during changing language
export const formatConsumptionType = (consumptionType: ConsumptionType) => {
  switch (consumptionType) {
    case ConsumptionType.MAC:
      return "Mise à consommation"
    case ConsumptionType.MAC_DECLASSEMENT:
      return "Déclassement"
  }
  return ""
}
