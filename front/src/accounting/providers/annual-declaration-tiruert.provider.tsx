import { createContext, ReactNode, useMemo, useContext } from "react"
import { useParams } from "react-router-dom"
import { useQuery } from "common/hooks/async"
import { getCurrentAnnualDeclaration } from "accounting/api/api"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"

export interface AnnualDeclarationTiruertContextValue {
  /** Current declaration year (returned by the API). */
  currentDeclarationYear: number | undefined

  /** Whether the selected year is in the currentdeclaration period */
  isDeclarationInCurrentPeriod: boolean

  selectedYear: number
}

export const AnnualDeclarationTiruertContext =
  createContext<AnnualDeclarationTiruertContextValue | null>(null)

interface AnnualDeclarationTiruertProviderProps {
  readonly children: ReactNode
}

/**
 * Provider pour le contexte de déclaration annuelle teneur (tiruert).
 * Expose l'année courante de déclaration et indique si elle correspond à l'année dans l'URL.
 */
export function AnnualDeclarationTiruertProvider({
  children,
}: AnnualDeclarationTiruertProviderProps) {
  const currentYear = new Date().getFullYear()
  const entity = useEntity()
  const selectedYear = useAnnualDeclarationTiruertYear()
  const { result, loading } = useQuery(getCurrentAnnualDeclaration, {
    key: "annual-declaration-tiruert",
    params: [entity.id],
  })
  // const parsedYear = useAnnualDeclarationTiruertYear()

  const currentDeclarationYear = result?.data?.year
  const year = selectedYear ?? currentYear
  const isDeclarationInCurrentPeriod = year
    ? new Date().getFullYear() === year + 1
    : false

  const value = useMemo<AnnualDeclarationTiruertContextValue>(
    () => ({
      currentDeclarationYear,
      isDeclarationInCurrentPeriod,
      selectedYear: year,
    }),
    [currentDeclarationYear, isDeclarationInCurrentPeriod, year]
  )

  if (loading) {
    return <LoaderOverlay />
  }

  return (
    <AnnualDeclarationTiruertContext.Provider value={value}>
      {children}
    </AnnualDeclarationTiruertContext.Provider>
  )
}

export function useAnnualDeclarationTiruert(): AnnualDeclarationTiruertContextValue {
  const ctx = useContext(AnnualDeclarationTiruertContext)
  if (!ctx) {
    throw new Error(
      "useAnnualDeclarationTiruertContext doit être utilisé dans un AnnualDeclarationTiruertProvider"
    )
  }
  return ctx
}

export function useAnnualDeclarationTiruertYear(): number | undefined {
  const { year: _year } = useParams<{ year: string }>()
  const parsedYear = _year ? parseInt(_year, 10) : undefined
  return parsedYear
}
