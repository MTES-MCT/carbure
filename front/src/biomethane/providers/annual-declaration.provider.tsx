import { createContext, ReactNode, useContext } from "react"
import { declarationInterval } from "biomethane/utils"

export interface AnnualDeclarationContextValue {
  year: number
  isInDeclarationPeriod: boolean
}

export const AnnualDeclarationContext =
  createContext<AnnualDeclarationContextValue | null>(null)

interface AnnualDeclarationProviderProps {
  children: ReactNode
  year: number
}

export function AnnualDeclarationProvider({
  children,
  year,
}: AnnualDeclarationProviderProps) {
  const isInDeclarationPeriod = year === declarationInterval.year

  const value: AnnualDeclarationContextValue = {
    year,
    isInDeclarationPeriod,
  }

  return (
    <AnnualDeclarationContext.Provider value={value}>
      {children}
    </AnnualDeclarationContext.Provider>
  )
}

export function useAnnualDeclaration(): AnnualDeclarationContextValue {
  const ctx = useContext(AnnualDeclarationContext)
  if (!ctx) {
    throw new Error(
      "useAnnualDeclaration doit être utilisé dans un AnnualDeclarationProvider"
    )
  }
  return ctx
}
