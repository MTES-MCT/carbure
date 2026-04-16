import { useMemo } from "react"
import { UnitType } from "biomethane/pages/production/types"
import { InstallationCategory } from "biomethane/pages/contract/types"
import { useBiomethaneProductionUnit } from "./use-biomethane-production-unit"
import { useBiomethaneContractInfos } from "./use-biomethane-contract-infos"

export interface BiomethaneBusinessRulesManager {
  shouldFillDigestate: boolean
}

export const useBiomethaneBusinessRules =
  (): BiomethaneBusinessRulesManager => {
    const { productionUnit } = useBiomethaneProductionUnit()
    const { contractInfos } = useBiomethaneContractInfos()

    return useMemo(
      () => ({
        shouldFillDigestate:
          productionUnit?.unit_type !== UnitType.ISDND &&
          contractInfos?.installation_category !==
            InstallationCategory.INSTALLATION_CATEGORY_3,
      }),
      [productionUnit?.unit_type, contractInfos?.installation_category]
    )
  }
