/**
 * Syncs the URL (hash #missing-fields) with the action that shows missing fields.
 * - Listens to the URL hash on the current page
 * - Triggers useShowMissingFields(form) when the anchor is present
 * - Clears the anchor right after (to avoid re-executions)
 */
import { FormManager } from "common/components/form2"
import { useShowMissingFields } from "./use-show-missing-fields"
import { useLocation, useNavigate } from "react-router"
import { useEffect } from "react"
import { MISSING_FIELDS_HASH } from "../missing-fields.constants"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const useMissingFields = <FormType extends object | undefined>(
  form: FormManager<FormType>
) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { showMissingFields } = useShowMissingFields(form)
  const { canEditDeclaration } = useAnnualDeclaration()
  useEffect(() => {
    if (canEditDeclaration && location.hash.includes(MISSING_FIELDS_HASH)) {
      showMissingFields()
      navigate({ hash: "" })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.hash])
}
