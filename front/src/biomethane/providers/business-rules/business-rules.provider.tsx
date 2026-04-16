import { createContext, ReactNode, useContext, useMemo } from "react"
import { useGetContractInfos } from "biomethane/pages/contract/contract.hooks"
import { useProductionUnit } from "biomethane/pages/production/production.hooks"
import { BiomethaneBusinessRulesManager, buildRules } from "./rules"

const BiomethaneBusinessRulesContext =
  createContext<BiomethaneBusinessRulesManager | null>(null)

const useConstructBiomethaneBusinessRules = (options?: {
  runQueries?: boolean
}) => {
  const { runQueries = false } = options ?? {}
  const { result: contractInfos } = useGetContractInfos({
    executeOnMount: runQueries,
  })
  const { result: productionUnit } = useProductionUnit({
    executeOnMount: runQueries,
  })

  const context = useMemo(
    () => ({ productionUnit, contractInfos }),
    [productionUnit, contractInfos]
  )

  const rules = useMemo(() => buildRules(context), [context])

  return { rules }
}
export const BiomethaneBusinessRulesProvider = ({
  children,
}: {
  readonly children: ReactNode
}) => {
  const { rules } = useConstructBiomethaneBusinessRules({
    runQueries: true,
  })

  return (
    <BiomethaneBusinessRulesContext.Provider value={rules}>
      {children}
    </BiomethaneBusinessRulesContext.Provider>
  )
}

export const useBiomethaneBusinessRules = () => {
  const rules = useContext(BiomethaneBusinessRulesContext)
  const context = useConstructBiomethaneBusinessRules({
    runQueries: !rules,
  })

  return rules ?? context.rules
}
