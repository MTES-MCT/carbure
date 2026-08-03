import type { TFunction } from "i18next"

import { FuelUsage } from "transactions/types"

export function getFuelUsageOptions(t: TFunction) {
  return [
    { value: FuelUsage.Road, label: t("Routier (éligible)") },
    { value: FuelUsage.Heating, label: t("Combustible (non éligible)") },
    { value: FuelUsage.Agriculture, label: t("Agricole (éligible)") },
    { value: FuelUsage.Construction, label: t("BTP (éligible)") },
    { value: FuelUsage.Maritime, label: t("Maritime (éligible)") },
    { value: FuelUsage.InlandWaterway, label: t("Fluvial (éligible)") },
    { value: FuelUsage.Rail, label: t("Ferroviaire (éligible)") },
    { value: FuelUsage.Fishing, label: t("Pêche (non éligible)") },
    { value: FuelUsage.Other, label: t("Autres (non éligible)") },
  ]
}
