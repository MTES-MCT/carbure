import { useMemo } from "react"
import { useBiomethaneProductionUnit } from "./use-biomethane-production-unit"
import { useBiomethaneContractInfos } from "./use-biomethane-contract-infos"
import {
  buildDigestateBusinessRules,
  DigestateBusinessRules,
} from "./business-rules/digestate.rules"
import { buildCommonRules } from "./business-rules/common"

export interface BiomethaneBusinessRulesManager {
  digestate: DigestateBusinessRules
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
      }),
      [context]
    )
  }
