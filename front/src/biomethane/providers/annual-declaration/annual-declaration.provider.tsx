import { createContext, ReactNode, useContext } from "react"
import { getAnnualDeclaration } from "biomethane/api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclaration, AnnualDeclarationStatus } from "biomethane/types"
import { useParams } from "react-router-dom"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export interface AnnualDeclarationContextValue {
  /** Selected year for the annual declaration */
  selectedYear: number

  /** Current annual declaration data for the entity */
  annualDeclaration?: AnnualDeclaration

  /** Whether the selected year is in the currentdeclaration period */
  isDeclarationInCurrentPeriod: boolean

  /** Whether the annual declaration has been validated/declared */
  isDeclarationValidated: boolean

  /** Whether the annual declaration can be edited */
  canEditDeclaration: boolean

  /** Whether the annual declaration has missing objects (digestate or energy) */
  hasAnnualDeclarationMissingObjects: boolean

  /** Whether at least one supply plan input (intrant) has been filled */
  hasAtLeastOneSupplyInput: boolean

  /** Key for the current annual declaration */
  annualDeclarationKey: string
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
  const { selectedEntityId } = useSelectedEntity()

  const { result: annualDeclaration, loading: loadingAnnualDeclaration } =
    useQuery(getAnnualDeclaration, {
      key,
      params: [entity.id, parsedYear, selectedEntityId],
    })

  if (loadingAnnualDeclaration && !annualDeclaration) return <LoaderOverlay />

  // Use year from url if provided, otherwise selected year is current year
  const year = parsedYear ?? currentYear

  const isDeclarationInCurrentPeriod = annualDeclaration?.year
    ? new Date().getFullYear() === annualDeclaration?.year + 1
    : false

  const isDeclarationValidated =
    annualDeclaration?.status === AnnualDeclarationStatus.DECLARED

  // For biomethane producers, the declaration can be edited if :
  // - it is not validated
  // - the declaration is open
  // - the entity has write rights
  const canEditDeclarationBiomethaneProducer =
    !isDeclarationValidated &&
    Boolean(annualDeclaration?.is_open) &&
    entity.canWrite()

  // For dreals, the declaration can't be edited
  const canEditDeclarationAdmin = false

  const canEditDeclaration = entity.isBiomethaneProducer
    ? canEditDeclarationBiomethaneProducer
    : canEditDeclarationAdmin

  const hasAnnualDeclarationMissingObjects =
    annualDeclaration?.missing_fields?.digestate_missing_fields === null ||
    annualDeclaration?.missing_fields?.energy_missing_fields === null

  // Check if at least one supply plan input has been filled
  const hasAtLeastOneSupplyInput =
    annualDeclaration?.missing_fields?.supply_plan_valid ?? false

  const value: AnnualDeclarationContextValue = {
    selectedYear: year,
    annualDeclaration,
    isDeclarationInCurrentPeriod,
    isDeclarationValidated,
    canEditDeclaration,
    hasAnnualDeclarationMissingObjects,
    hasAtLeastOneSupplyInput,
    annualDeclarationKey: key,
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
