import { createContext, ReactNode, useContext } from "react"
import { getCurrentAnnualDeclaration } from "biomethane/api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclaration } from "biomethane/types"
import { useParams } from "react-router-dom"

export interface AnnualDeclarationContextValue {
  selectedYear: number
  currentAnnualDeclaration: AnnualDeclaration
  isInDeclarationPeriod: boolean
}

export const AnnualDeclarationContext =
  createContext<AnnualDeclarationContextValue | null>(null)

interface AnnualDeclarationProviderProps {
  children: ReactNode
}

const currentYear = new Date().getFullYear()

export function AnnualDeclarationProvider({
  children,
}: AnnualDeclarationProviderProps) {
  const entity = useEntity()
  const {
    result: currentAnnualDeclaration,
    loading: loadingCurrentAnnualDeclaration,
  } = useQuery(getCurrentAnnualDeclaration, {
    key: "current-annual-declaration",
    params: [entity.id],
  })
  const { year: _year } = useParams<{ year: string }>()

  if (loadingCurrentAnnualDeclaration && !currentAnnualDeclaration)
    return <LoaderOverlay />

  if (!currentAnnualDeclaration) return null

  // Use year from url if provided, otherwise selected year is current year
  const year = _year ? parseInt(_year) : currentYear
  const isInDeclarationPeriod = year === currentAnnualDeclaration?.year

  const value: AnnualDeclarationContextValue = {
    selectedYear: year,
    currentAnnualDeclaration,
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
