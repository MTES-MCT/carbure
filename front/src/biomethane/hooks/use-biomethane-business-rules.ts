import { useMemo } from "react"
import { useBiomethaneProductionUnit } from "./use-biomethane-production-unit"
import { useBiomethaneContractInfos } from "./use-biomethane-contract-infos"
import {
  buildDigestateBusinessRules,
  DigestateBusinessRules,
} from "./business-rules/digestate.rules"
import {
  buildCommonRules,
  CommonBusinessRules,
} from "./business-rules/common.rules"
import {
  buildProductionRules,
  ProductionBusinessRules,
} from "./business-rules/production.rules"

export interface BiomethaneBusinessRulesManager {
  digestate: DigestateBusinessRules
  common: CommonBusinessRules
  production: ProductionBusinessRules
}

/**
 * Biomethane business rules are domain eligibility rules,
 * not user authorization permissions.
 *
 * ex: `shouldFillDigestate` tells whether Digestate declaration
 * must be completed for the selected entity/year context.
 *
 */
export const useBiomethaneBusinessRules =
  (): BiomethaneBusinessRulesManager => {
    const { productionUnit } = useBiomethaneProductionUnit()
    const { contractInfos } = useBiomethaneContractInfos()

    const context = useMemo(
      () => ({
        productionUnit,
        contractInfos,
      }),
      [productionUnit, contractInfos]
    )

    return useMemo(
      () => ({
        digestate: buildDigestateBusinessRules(context),
        common: buildCommonRules(context),
        production: buildProductionRules(context),
      }),
      [context]
    )
  }
