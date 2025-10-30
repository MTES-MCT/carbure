/**
 * Builds i18n messages (JSX) describing missing fields per page.
 * - Computes counts per page and generates links to the #missing-fields anchor
 * - Also returns the counts for conditional rendering in the parent component
 */
import { useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { useRoutes } from "common/hooks/routes"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { MISSING_FIELDS_HASH } from "../missing-fields.constants"
import { useMissingFieldCounts } from "./use-missing-fields-helpers"

export const useMissingFieldsMessages = ({
  onPageClick,
}: {
  onPageClick?: (page: string) => void
} = {}) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { selectedYear } = useAnnualDeclaration()
  const { digestateCount, energyCount } = useMissingFieldCounts()

  const biomethaneRoutes = routes.BIOMETHANE(selectedYear)

  const errorMessage = useMemo(() => {
    const pages: { page: string; count: number; url: string }[] = []

    const generateTranslatedMessage = (
      page: string,
      count: number,
      url: string,
      message: string
    ) => {
      return (
        <Trans
          defaults={message}
          values={{ count, page }}
          components={{
            strong: <strong />,
            CustomLink: (
              // @ts-ignore children is propagé au bouton par i18next
              <Button
                customPriority="link"
                linkProps={{
                  to: `${url}#${MISSING_FIELDS_HASH}`,
                  onClick: () => onPageClick?.(page),
                }}
              />
            ),
          }}
          key={page}
          t={t}
        />
      )
    }

    const messages = [
      (page: string, count: number, url: string) => {
        const missingFieldsFirstMessage = t(
          "Champs manquants : il y a <strong>{{count}} champs manquants</strong> dans la page <CustomLink>{{page}}</CustomLink>",
          {
            count,
            page,
          }
        )
        return generateTranslatedMessage(
          page,
          count,
          url,
          missingFieldsFirstMessage
        )
      },
      (page: string, count: number, url: string) => {
        const missingFieldsAdditionalMessage = t(
          " et <strong>{{count}} champs manquants</strong> dans la page <CustomLink>{{page}}</CustomLink>",
          {
            page,
            count,
          }
        )
        return generateTranslatedMessage(
          page,
          count,
          url,
          missingFieldsAdditionalMessage
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
    onPageClick,
  ])

  return { errorMessage, digestateCount, energyCount }
}
