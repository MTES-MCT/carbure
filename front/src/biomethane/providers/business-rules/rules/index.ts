import { BiomethaneRulesContext } from "../types"
import { buildCommonRules, CommonBusinessRules } from "./common.rules"
import {
  buildDigestateBusinessRules,
  DigestateBusinessRules,
} from "./digestate.rules"
import { buildEnergyRules, EnergyBusinessRules } from "./energy.rules"
import {
  buildProductionRules,
  ProductionBusinessRules,
} from "./production.rules"
export * from "./common.rules"
export * from "./digestate.rules"
export * from "./production.rules"
export * from "./energy.rules"

export interface BiomethaneBusinessRulesManager {
  digestate: DigestateBusinessRules
  common: CommonBusinessRules
  production: ProductionBusinessRules
  energy: EnergyBusinessRules
}

export const buildRules = (
  context: BiomethaneRulesContext
): BiomethaneBusinessRulesManager => {
  return {
    digestate: buildDigestateBusinessRules(context),
    common: buildCommonRules(context),
    production: buildProductionRules(context),
    energy: buildEnergyRules(context),
  }
}
