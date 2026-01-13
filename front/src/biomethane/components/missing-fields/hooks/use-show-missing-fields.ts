/**
 * Orchestrates the display of missing fields for the current page.
 * - Resolves current page (Digestate/Energy) and the list of missing fields
 * - Registers/expands affected sections via SectionsManager
 * - Sets validation errors on form fields
 * - Focuses the first missing field present in the DOM
 */
import { useCallback } from "react"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useSectionsManager } from "common/providers/sections-manager.provider"
import { getMissingFieldsSectionIds } from "../missing-fields.config"
import { focusFirstMissingField } from "../missing-fields.utils"
import { pageToMissingFieldKey } from "../missing-fields.constants"
import { usePageDetection } from "./use-page-detection"
import type { FormManager } from "common/components/form2"

export const useShowMissingFields = <FormType extends object | undefined>(
  form: FormManager<FormType>
) => {
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const sectionsManager = useSectionsManager()
  const { currentPage } = usePageDetection()
  const { t } = useTranslation()

  const showMissingFields = useCallback(() => {
    if (!currentPage) {
      console.error(
        "Missing fields can only be displayed on digestate or energy page"
      )
      return
    }

    const missingFields =
      currentAnnualDeclaration?.missing_fields?.[
        pageToMissingFieldKey[currentPage]
      ] ?? []

    const sectionIds = getMissingFieldsSectionIds(missingFields)
    sectionIds.forEach((sectionId) => {
      sectionsManager.registerSection(sectionId, true)
      sectionsManager.setSectionExpanded(sectionId, true)
    })

    missingFields.forEach((field) => {
      form.setFieldError(field as keyof FormType, t("Ce champ est obligatoire"))
    })

    if (missingFields.length > 0) {
      focusFirstMissingField(missingFields)
    }
  }, [
    currentPage,
    currentAnnualDeclaration?.missing_fields,
    sectionsManager,
    form,
    t,
  ])

  return { showMissingFields }
}
