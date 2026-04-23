import { buildCommonRules } from "./common.rules"
import { BiomethaneRulesContext } from "../types"

export interface EnergyBusinessRules {
  installationEnergyNeeds: {
    displaySection: boolean
  }
  energyEfficiency: {
    displaySelfConsumedBiogasOrBiomethaneField: boolean
  }
}

export const buildEnergyRules = (
  ctx: BiomethaneRulesContext
): EnergyBusinessRules => {
  const commonRules = buildCommonRules(ctx)

  return {
    installationEnergyNeeds: {
      displaySection: !commonRules.isTariffReference2011Or2020Or2021,
    },
    energyEfficiency: {
      displaySelfConsumedBiogasOrBiomethaneField:
        !commonRules.isTariffReference2011Or2020Or2021,
    },
  }
}
