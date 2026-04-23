import { createContext, ReactNode, useContext, useMemo } from "react"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import { BiomethaneProductionUnit } from "biomethane/pages/production/types"
import { SettingsNotFilled } from "biomethane/components/settings-not-filled"
import { useAnnualDeclaration } from "../annual-declaration"
import { useBiomethaneProductionUnit } from "biomethane/hooks/use-biomethane-production-unit"
import { useBiomethaneContractInfos } from "biomethane/hooks/use-biomethane-contract-infos"

export interface ContractProductionUnitContextValue {
  /** Contract information for the entity */
  contractInfos: BiomethaneContract | undefined
  /** Production unit information for the entity */
  productionUnit: BiomethaneProductionUnit | undefined
  /** Whether contract data is loading */
  loadingContract: boolean
  /** Whether production unit data is loading */
  loadingProductionUnit: boolean
  /** Whether any data is loading */
  loading: boolean
}

export const ContractProductionUnitContext =
  createContext<ContractProductionUnitContextValue | null>(null)

interface ContractProductionUnitProviderProps {
  readonly children: ReactNode

  // Whether to allow empty contract and production unit data
  readonly allowEmpty?: boolean
}

/**
 * Provider for managing contract and production unit context.
 *
 * This provider centralizes the business logic related to contracts and production units:
 * - Fetches the contract information for the entity
 * - Fetches the production unit information for the entity
 * - Provides a global context with all necessary data for child components
 *
 * Child components can access this data via the useContractProductionUnit() hook.
 */
export function ContractProductionUnitProvider({
  children,
  allowEmpty = false,
}: ContractProductionUnitProviderProps) {
  const { contractInfos, loadingContract } = useBiomethaneContractInfos()
  const { productionUnit, loadingProductionUnit } =
    useBiomethaneProductionUnit()
  const { annualDeclarationMissingFieldsData } = useAnnualDeclaration()

  const loading = loadingContract || loadingProductionUnit

  const value = useMemo(
    () => ({
      contractInfos,
      productionUnit,
      loadingContract,
      loadingProductionUnit,
      loading,
    }),
    [
      contractInfos,
      productionUnit,
      loadingContract,
      loadingProductionUnit,
      loading,
    ]
  )

  if (
    !allowEmpty &&
    !loading &&
    annualDeclarationMissingFieldsData.hasBiomethaneSettingsMissingObjects
  )
    return <SettingsNotFilled />

  return (
    <ContractProductionUnitContext.Provider value={value}>
      {children}
    </ContractProductionUnitContext.Provider>
  )
}

export function useContractProductionUnit(): ContractProductionUnitContextValue {
  const ctx = useContext(ContractProductionUnitContext)
  if (!ctx) {
    throw new Error(
      "useContractProductionUnit doit être utilisé dans un ContractProductionUnitProvider"
    )
  }
  return ctx
}
