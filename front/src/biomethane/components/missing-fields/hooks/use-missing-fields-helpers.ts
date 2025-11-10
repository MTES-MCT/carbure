/**
 * Exposes helper hooks related to missing fields.
 * - useMissingFieldCounts: computes the number of missing fields per page (Digestate / Energy)
 *   from the current AnnualDeclaration.
 * - useNavigateToMissingFields: provides navigation to the #missing-fields anchor
 *   to trigger the automatic display of missing fields.
 */
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useCallback } from "react"
import { useNavigate } from "react-router"
import { MISSING_FIELDS_HASH } from "../missing-fields.constants"

export const useMissingFieldCounts = () => {
  const { currentAnnualDeclaration } = useAnnualDeclaration()

  const digestateCount =
    currentAnnualDeclaration.missing_fields?.digestate_missing_fields?.length ??
    0
  const energyCount =
    currentAnnualDeclaration.missing_fields?.energy_missing_fields?.length ?? 0

  return { digestateCount, energyCount }
}

export const useNavigateToMissingFields = () => {
  const navigate = useNavigate()

  const navigateToMissingFields = useCallback(() => {
    navigate({ hash: `${MISSING_FIELDS_HASH}` })
  }, [navigate])

  return { navigateToMissingFields }
}
