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

  const isISDNDInstallationAndNot2011Or2020Or2021 =
    commonRules.isISDNDInstallation &&
    !commonRules.isTariffReference2011Or2020Or2021

  return {
    installationEnergyNeeds: {
      // Display section if not ISDND installation or if ISDND installation and not 2011, 2020 or 2021 tariff reference
      displaySection:
        !commonRules.isISDNDInstallation ||
        isISDNDInstallationAndNot2011Or2020Or2021,
    },
    energyEfficiency: {
      displaySelfConsumedBiogasOrBiomethaneField:
        !commonRules.isISDNDInstallation ||
        isISDNDInstallationAndNot2011Or2020Or2021,
    },
  }
}
