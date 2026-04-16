import { buildCommonRules } from "./common.rules"
import { BiomethaneRulesContext } from "../types"

export interface ProductionBusinessRules {
  productionSite: {
    displayProcessType: boolean
    displayMethanizationProcess: boolean
    displayHygienizationUnit: boolean
  }
  digestateProcessing: {
    displaySection: boolean
  }
  digestateStorage: {
    displaySection: boolean
  }
}

export const buildProductionRules = (
  ctx: BiomethaneRulesContext
): ProductionBusinessRules => {
  const commonRules = buildCommonRules(ctx)

  return {
    productionSite: {
      displayProcessType: !commonRules.isISDNDInstallation,
      displayMethanizationProcess: !commonRules.isISDNDInstallation,
      displayHygienizationUnit: !commonRules.isISDNDInstallation,
    },
    digestateProcessing: {
      displaySection: !commonRules.isISDNDInstallation,
    },
    digestateStorage: {
      displaySection: !commonRules.isISDNDInstallation,
    },
  }
}
