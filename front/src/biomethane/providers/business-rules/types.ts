import { BiomethaneContract } from "biomethane/pages/contract/types"
import { BiomethaneProductionUnit } from "biomethane/pages/production/types"

export interface BiomethaneRulesContext {
  productionUnit?: BiomethaneProductionUnit
  contractInfos?: BiomethaneContract
}
