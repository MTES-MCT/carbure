import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclaration } from "biomethane/types"
import { Button } from "common/components/button2"
import { FormManager } from "common/components/form2"
import { useCallback, useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation } from "react-router-dom"
import { getMissingFieldsSectionIds } from "./missing-fields.config"
import { useSectionsManager } from "common/providers/sections-manager.provider"
import { focusMissingField } from "./missing-fields.utils"
import { useRoutes } from "common/hooks/routes"

enum Page {
  DIGESTATE = "digestate",
  ENERGY = "energy",
}

const usePageDetection = () => {
  const location = useLocation()

  const isDigestatePage = location.pathname.includes(Page.DIGESTATE)
  const isEnergyPage = location.pathname.includes(Page.ENERGY)
  const currentPage = isDigestatePage
    ? Page.DIGESTATE
    : isEnergyPage
      ? Page.ENERGY
      : undefined

  return {
    isDigestatePage,
    isEnergyPage,
    currentPage,
  }
}

const mapping: Record<Page, keyof AnnualDeclaration["missing_fields"]> = {
  [Page.DIGESTATE]: "digestate_missing_fields",
  [Page.ENERGY]: "energy_missing_fields",
}
/**
 * Hook to get missing fields for a given page
 * Warning : useMissingFields is used in the common page header and we don't know the type of the form
 * @param form - The form manager
 * @returns The missing fields for the given page and a function to show the missing fields
 */
const useMissingFields = <FormType extends object | undefined>(
  form: FormManager<FormType>
) => {
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const { t } = useTranslation()
  const { currentPage } = usePageDetection()
  const sectionsManager = useSectionsManager()

  const showMissingFields = useCallback(() => {
    if (!currentPage) {
      console.error(
        "Missing fields can only be displayed on digestate or energy page"
      )
      return
    }
    const missingFields =
      currentAnnualDeclaration.missing_fields?.[mapping[currentPage]] ?? []

    // Get the section ids that have missing fields
    const sectionIds = getMissingFieldsSectionIds(missingFields)
    sectionIds.forEach((sectionId) => {
      sectionsManager.registerSection(sectionId, true)
    })

    missingFields.forEach((field) => {
      form.setFieldError(field as keyof FormType, t("Ce champ est obligatoire"))
    })

    if (missingFields.length > 0) {
      const firstMissingField = missingFields[0]
      focusMissingField(firstMissingField)
    }
  }, [
    currentPage,
    currentAnnualDeclaration.missing_fields,
    sectionsManager,
    form,
    t,
  ])

  return {
    showMissingFields,
    digestateCount:
      currentAnnualDeclaration.missing_fields?.digestate_missing_fields
        ?.length ?? 0,
    energyCount:
      currentAnnualDeclaration.missing_fields?.energy_missing_fields?.length ??
      0,
  }
}

export const useMissingFieldsMessages = <FormType extends object | undefined>(
  form: FormManager<FormType>
) => {
  const { t } = useTranslation()
  const { digestateCount, energyCount, showMissingFields } =
    useMissingFields(form)
  const routes = useRoutes()
  const { selectedYear } = useAnnualDeclaration()

  const biomethaneRoutes = routes.BIOMETHANE(selectedYear)

  const errorMessage = useMemo(() => {
    const pages: { page: string; count: number; url: string }[] = []
    const messages = [
      (page: string, count: number, url: string) => {
        const missingFieldsFirstMessage = t(
          "Champs manquants : il y a <strong>{{count}} champs manquants</strong> dans la section <CustomLink>{{page}}</CustomLink>",
          {
            count,
            page,
          }
        )
        return (
          <Trans
            defaults={missingFieldsFirstMessage}
            values={{ count, page }}
            components={{
              strong: <strong />,
              CustomLink: (
                // @ts-ignore children is propagated to the button by i18next
                <Button
                  customPriority="link"
                  linkProps={{ to: `${url}#missing-fields` }}
                />
              ),
            }}
            key={page}
            t={t}
          />
        )
      },
      (page: string, count: number, url: string) => {
        const missingFieldsAdditionalMessage = t(
          " et <strong>{{count}} champs manquants</strong> dans la section <CustomLink>{{page}}</CustomLink>",
          {
            page,
            count,
          }
        )

        return (
          <Trans
            defaults={missingFieldsAdditionalMessage}
            values={{ count, page, url }}
            components={{
              strong: <strong />,
              CustomLink: (
                // @ts-ignore children is propagated to the button by i18next
                <Button
                  customPriority="link"
                  linkProps={{ to: `${url}#missing-fields` }}
                />
              ),
            }}
            key={page}
            t={t}
          />
        )
      },
    ]
    if (digestateCount > 0)
      pages.push({
        page: t("Digestat"),
        count: digestateCount,
        url: biomethaneRoutes.DIGESTATE,
      })
    if (energyCount > 0)
      pages.push({
        page: t("Energie"),
        count: energyCount,
        url: biomethaneRoutes.ENERGY,
      })

    return pages.map(({ page, count, url }, index) =>
      messages[index]?.(page, count, url)
    )
  }, [
    digestateCount,
    energyCount,
    t,
    biomethaneRoutes.DIGESTATE,
    biomethaneRoutes.ENERGY,
  ])

  return { errorMessage, digestateCount, energyCount, showMissingFields }
}
