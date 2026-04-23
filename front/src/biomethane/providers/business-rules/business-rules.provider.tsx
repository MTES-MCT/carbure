import { createContext, ReactNode, useContext, useMemo } from "react"
import { useGetContractInfos } from "biomethane/pages/contract/contract.hooks"
import { useProductionUnit } from "biomethane/pages/production/production.hooks"
import { BiomethaneBusinessRulesManager, buildRules } from "./rules"
import { LoaderOverlay } from "common/components/scaffold"

const BiomethaneBusinessRulesContext =
  createContext<BiomethaneBusinessRulesManager | null>(null)

const useConstructBiomethaneBusinessRules = (options?: {
  runQueries?: boolean
}) => {
  const { runQueries = false } = options ?? {}
  const { result: contractInfos, loading: loadingContract } =
    useGetContractInfos({
      executeOnMount: runQueries,
    })
  const { result: productionUnit, loading: loadingProductionUnit } =
    useProductionUnit({
      executeOnMount: runQueries,
    })

  const context = useMemo(
    () => ({ productionUnit, contractInfos }),
    [productionUnit, contractInfos]
  )

  const rules = useMemo(() => buildRules(context), [context])

  return { rules, loading: loadingContract || loadingProductionUnit }
}
export const BiomethaneBusinessRulesProvider = ({
  children,
}: {
  readonly children: ReactNode
}) => {
  const { rules, loading } = useConstructBiomethaneBusinessRules({
    runQueries: true,
  })

  if (loading) return <LoaderOverlay />

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
