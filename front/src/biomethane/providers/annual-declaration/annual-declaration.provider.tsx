import { createContext, ReactNode, useContext } from "react"
import { getCurrentAnnualDeclaration } from "biomethane/api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclaration, AnnualDeclarationStatus } from "biomethane/types"
import { useParams } from "react-router"

export interface AnnualDeclarationContextValue {
  /** Selected year for the annual declaration */
  selectedYear: number
  /** Current annual declaration data for the entity */
  currentAnnualDeclaration: AnnualDeclaration
  /** Whether we are in the declaration period */
  isInDeclarationPeriod: boolean
  /** Whether the annual declaration has been validated/declared */
  isDeclarationValidated: boolean
  /** Whether the annual declaration can be edited */
  canEditDeclaration: boolean

  /** Whether the annual declaration has missing objects (digestate or energy) */
  hasAnnualDeclarationMissingObjects: boolean
}

export const AnnualDeclarationContext =
  createContext<AnnualDeclarationContextValue | null>(null)

interface AnnualDeclarationProviderProps {
  children: ReactNode
}

/**
 * Provider for managing biomethane annual declaration context.
 *
 * This provider centralizes the business logic related to annual declarations:
 * - Fetches the current annual declaration for the entity
 * - Determines the selected year (from URL or current year)
 * - Calculates edit permissions based on status and entity rights
 * - Provides a global context with all necessary data for child components
 *
 * Child components can access this data via the useAnnualDeclaration() hook.
 */
export function AnnualDeclarationProvider({
  children,
}: AnnualDeclarationProviderProps) {
  // We need to use the current year inside the provider to mock the date when the provider is mounted
  const currentYear = new Date().getFullYear()
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
  const isDeclarationValidated =
    currentAnnualDeclaration?.status === AnnualDeclarationStatus.DECLARED
  const canEditDeclaration =
    !isDeclarationValidated && isInDeclarationPeriod && entity.canWrite()
  const hasAnnualDeclarationMissingObjects =
    currentAnnualDeclaration?.missing_fields?.digestate_missing_fields ===
      null ||
    currentAnnualDeclaration?.missing_fields?.energy_missing_fields === null

  const value: AnnualDeclarationContextValue = {
    selectedYear: year,
    currentAnnualDeclaration,
    isInDeclarationPeriod,
    isDeclarationValidated,
    canEditDeclaration,
    hasAnnualDeclarationMissingObjects,
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
