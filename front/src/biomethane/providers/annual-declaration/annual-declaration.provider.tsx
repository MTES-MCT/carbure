import { createContext, ReactNode, useContext } from "react"
import { getCurrentAnnualDeclaration } from "biomethane/api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclaration, AnnualDeclarationStatus } from "biomethane/types"
import { useParams } from "react-router-dom"

export interface AnnualDeclarationContextValue {
  /** Selected year for the annual declaration */
  selectedYear: number
  /** Current annual declaration data for the entity */
  currentAnnualDeclaration?: AnnualDeclaration
  /** Whether we are in the declaration period */
  isInDeclarationPeriod: boolean
  /** Whether the annual declaration has been validated/declared */
  isDeclarationValidated: boolean
  /** Whether the annual declaration can be edited */
  canEditDeclaration: boolean

  /** Whether the annual declaration has missing objects (digestate or energy) */
  hasAnnualDeclarationMissingObjects: boolean

  /** Whether at least one supply plan input (intrant) has been filled */
  hasAtLeastOneSupplyInput: boolean

  /** Key for the current annual declaration */
  currentAnnualDeclarationKey: string
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
  const parsedYear = useAnnualDeclarationYear()

  const key =
    "current-annual-declaration" + (parsedYear ? `-${parsedYear}` : "")
  // We need to use the current year inside the provider to mock the date when the provider is mounted
  const currentYear = new Date().getFullYear()
  const entity = useEntity()
  const {
    result: currentAnnualDeclaration,
    loading: loadingCurrentAnnualDeclaration,
  } = useQuery(getCurrentAnnualDeclaration, {
    key,
    params: [entity.id, parsedYear],
  })

  if (loadingCurrentAnnualDeclaration && !currentAnnualDeclaration)
    return <LoaderOverlay />

  // Use year from url if provided, otherwise selected year is current year
  const year = parsedYear ?? currentYear

  const isInDeclarationPeriod = year === currentAnnualDeclaration?.year
  const isDeclarationValidated =
    currentAnnualDeclaration?.status === AnnualDeclarationStatus.DECLARED
  const canEditDeclaration =
    !isDeclarationValidated &&
    Boolean(currentAnnualDeclaration?.is_open) &&
    entity.canWrite()
  const hasAnnualDeclarationMissingObjects =
    currentAnnualDeclaration?.missing_fields?.digestate_missing_fields ===
      null ||
    currentAnnualDeclaration?.missing_fields?.energy_missing_fields === null

  // Check if at least one supply plan input has been filled
  const hasAtLeastOneSupplyInput =
    currentAnnualDeclaration?.missing_fields?.supply_plan_valid ?? false

  const value: AnnualDeclarationContextValue = {
    selectedYear: year,
    currentAnnualDeclaration,
    isInDeclarationPeriod,
    isDeclarationValidated,
    canEditDeclaration,
    hasAnnualDeclarationMissingObjects,
    hasAtLeastOneSupplyInput,
    currentAnnualDeclarationKey: key,
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

export function useAnnualDeclarationYear(): number | undefined {
  const { year: _year } = useParams<{ year: string }>()
  const parsedYear = _year ? parseInt(_year) : undefined
  return parsedYear
}
