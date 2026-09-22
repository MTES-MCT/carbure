import { Normalizer } from "common/utils/normalize"
import type { TFunction } from "i18next"

import { FuelUsage } from "transactions/types"

export const FUEL_USAGES: FuelUsage[] = [
  FuelUsage.Road,
  FuelUsage.Combustible,
  FuelUsage.Agriculture,
  FuelUsage.Construction,
  FuelUsage.Maritime,
  FuelUsage.InlandWaterway,
  FuelUsage.Rail,
  FuelUsage.Fishing,
  FuelUsage.Other,
]

export const getFuelUsageNormalizer = (t: TFunction): Normalizer<FuelUsage> => {
  const labels: Record<FuelUsage, string> = {
    [FuelUsage.Road]: t("Routier (éligible)"),
    [FuelUsage.Combustible]: t("Combustible (non éligible)"),
    [FuelUsage.Agriculture]: t("Agricole (éligible)"),
    [FuelUsage.Construction]: t("BTP (éligible)"),
    [FuelUsage.Maritime]: t("Maritime (éligible)"),
    [FuelUsage.InlandWaterway]: t("Fluvial (éligible)"),
    [FuelUsage.Rail]: t("Ferroviaire (éligible)"),
    [FuelUsage.Fishing]: t("Pêche (non éligible)"),
    [FuelUsage.Other]: t("Autres (non éligible)"),
  }

  return (usage) => ({
    value: usage,
    label: labels[usage],
  })
}
