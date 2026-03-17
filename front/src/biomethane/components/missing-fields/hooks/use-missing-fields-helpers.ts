/**
 * Exposes helper hooks related to missing fields.
 * - useMissingFieldCounts: computes the number of missing fields per page (Digestate / Energy)
 *   from the current AnnualDeclaration.
 * - useNavigateToMissingFields: provides navigation to the #missing-fields anchor
 *   to trigger the automatic display of missing fields.
 */
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { MISSING_FIELDS_HASH } from "../missing-fields.constants"

export const useMissingFieldCounts = () => {
  const { annualDeclaration } = useAnnualDeclaration()

  const digestateCount =
    annualDeclaration?.missing_fields?.digestate_missing_fields?.length ?? 0
  const energyCount =
    annualDeclaration?.missing_fields?.energy_missing_fields?.length ?? 0
  const contractCount =
    annualDeclaration?.missing_fields?.contract_missing_fields?.length ?? 0
  const productionUnitCount =
    annualDeclaration?.missing_fields?.production_unit_missing_fields?.length ??
    0
  const injectionCount =
    annualDeclaration?.missing_fields?.injection_missing_fields?.length ?? 0

  return {
    digestateCount,
    energyCount,
    contractCount,
    productionUnitCount,
    injectionCount,
    hasDigestateObject:
      annualDeclaration?.missing_fields?.digestate_missing_fields !== null,
    hasEnergyObject:
      annualDeclaration?.missing_fields?.energy_missing_fields !== null,
    hasContractObject:
      annualDeclaration?.missing_fields?.contract_missing_fields !== null,
    hasProductionUnitObject:
      annualDeclaration?.missing_fields?.production_unit_missing_fields !==
      null,
    hasInjectionObject:
      annualDeclaration?.missing_fields?.injection_missing_fields !== null,
  }
}

export const useNavigateToMissingFields = () => {
  const navigate = useNavigate()

  const navigateToMissingFields = useCallback(() => {
    navigate({ hash: `${MISSING_FIELDS_HASH}` })
  }, [navigate])

  return { navigateToMissingFields }
}
