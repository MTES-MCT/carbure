/**
 * Orchestrates the display of missing fields for the current page.
 * - Resolves current page (Digestate/Energy) and the list of missing fields
 * - Registers/expands affected sections via SectionsManager
 * - Sets validation errors on form fields
 * - Focuses the first missing field present in the DOM
 */
import { useCallback, useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useSectionsManager } from "common/providers/sections-manager.provider"
import {
  getMissingFieldConfig,
  getMissingFieldsSectionIds,
  getFieldNamesForSection,
  type BiomethaneSectionId,
} from "../missing-fields.config"
import {
  focusFirstMissingField,
  scrollToSection,
} from "../missing-fields.utils"
import { pageToMissingFieldKey } from "../missing-fields.constants"
import { usePageDetection } from "./use-page-detection"
import type { FormManager } from "common/components/form2"

export const useShowMissingFields = <FormType extends object | undefined>(
  form: FormManager<FormType>
) => {
  const { annualDeclaration } = useAnnualDeclaration()
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
      annualDeclaration?.missing_fields?.[pageToMissingFieldKey[currentPage]] ??
      []

    const sectionIds = getMissingFieldsSectionIds(missingFields)
    sectionIds.forEach((sectionId) => {
      sectionsManager.registerSection(sectionId, true)
      sectionsManager.setSectionExpanded(sectionId, true)
    })

    missingFields.forEach((field) => {
      form.setFieldError(field as keyof FormType, t("Ce champ est obligatoire"))
    })

    if (missingFields.length > 0) {
      const firstMissingField = missingFields[0]
      if (!firstMissingField) return
      const firstMissingFieldConfig = getMissingFieldConfig(firstMissingField)

      // Focus the first missing field if it is a direct field
      if (firstMissingFieldConfig?.field.type === "field") {
        focusFirstMissingField(missingFields)
      }

      // Otherwise scroll to the section and highlight it
      if (firstMissingFieldConfig?.field.type === "section") {
        scrollToSection(firstMissingFieldConfig.sectionId)
        sectionsManager.setSectionError(firstMissingFieldConfig.sectionId, true)
      }
    }
  }, [currentPage, annualDeclaration?.missing_fields, sectionsManager, form, t])

  useClearSectionErrors()

  return { showMissingFields }
}

/**
 * When missing_fields changes, clears section error for any section whose fields
 * are no longer in the missing list.
 */
const useClearSectionErrors = () => {
  const { annualDeclaration } = useAnnualDeclaration()
  const sectionsManager = useSectionsManager()
  const sectionsManagerRef = useRef(sectionsManager)
  sectionsManagerRef.current = sectionsManager
  const { currentPage } = usePageDetection()

  useEffect(() => {
    if (!annualDeclaration || !currentPage) return

    const { sections, setSectionError } = sectionsManagerRef.current
    const missingFields =
      annualDeclaration?.missing_fields?.[pageToMissingFieldKey[currentPage]] ??
      []
    const missingFieldsSet = new Set(missingFields)

    Object.entries(sections).forEach(([sectionId, sectionState]) => {
      if (!sectionState?.isError) return

      const fieldNamesInSection = getFieldNamesForSection(
        sectionId as BiomethaneSectionId
      )
      const hasAnyStillMissing = fieldNamesInSection.some((name) =>
        missingFieldsSet.has(name)
      )
      if (!hasAnyStillMissing) {
        setSectionError(sectionId, false)
      }
    })
  }, [annualDeclaration, currentPage])
}
