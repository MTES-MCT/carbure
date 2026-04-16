import { BiomethaneRulesContext } from "./types"
import { UnitType } from "biomethane/pages/production/types"
import { InstallationCategory } from "biomethane/pages/contract/types"

export interface CommonBusinessRules {
  isISDNDInstallation: boolean
}

export const buildCommonRules = (
  ctx: BiomethaneRulesContext
): CommonBusinessRules => {
  return {
    isISDNDInstallation:
      ctx.productionUnit?.unit_type === UnitType.ISDND ||
      ctx.contractInfos?.installation_category ===
        InstallationCategory.INSTALLATION_CATEGORY_3,
  }
}
