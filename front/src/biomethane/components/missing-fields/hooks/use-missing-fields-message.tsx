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

const generateNoObjectMessage = (
  page: string,
  url: string,
  message: string,
  onPageClick?: (page: string) => void
) => {
  return (
    <span>
      <Trans
        defaults={message}
        components={{
          CustomLink: (
            // @ts-ignore children is propagated to the button by i18next
            <Button
              customPriority="link"
              linkProps={{
                to: url,
                onClick: () => onPageClick?.(page),
              }}
            />
          ),
        }}
      />
    </span>
  )
}

const generateTranslatedMessage = (
  page: string,
  count: number,
  url: string,
  message: string,
  onPageClick?: (page: string) => void
) => {
  return (
    <span>
      <Trans
        defaults={message}
        values={{ count, page }}
        components={{
          strong: <strong />,
          CustomLink: (
            // @ts-ignore children is propagated to the button by i18next
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
        is="span"
      />
    </span>
  )
}

export const useMissingFieldsMessages = ({
  onPageClick,
}: {
  onPageClick?: (page: string) => void
} = {}) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { selectedYear, hasAtLeastOneSupplyInput } = useAnnualDeclaration()
  const { digestateCount, energyCount, hasDigestateObject, hasEnergyObject } =
    useMissingFieldCounts()

  const biomethaneRoutes = routes.BIOMETHANE(selectedYear)

  const digestateMessage = useMemo(() => {
    if (!hasDigestateObject)
      return generateNoObjectMessage(
        t("Digestat"),
        biomethaneRoutes.PRODUCER.DIGESTATE,
        t(
          "<CustomLink>{{page}}</CustomLink> : veuillez renseigner les différents champs de la page.",
          {
            page: t("Digestat"),
          }
        ),
        onPageClick
      )

    if (digestateCount === 0) return null
    return generateTranslatedMessage(
      t("Digestat"),
      digestateCount,
      biomethaneRoutes.PRODUCER.DIGESTATE,
      t(
        "<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>.",
        {
          count: digestateCount,
          page: t("Digestat"),
        }
      ),
      onPageClick
    )
  }, [
    digestateCount,
    biomethaneRoutes.PRODUCER.DIGESTATE,
    onPageClick,
    t,
    hasDigestateObject,
  ])

  const energyMessage = useMemo(() => {
    if (!hasEnergyObject)
      return generateNoObjectMessage(
        t("Energie"),
        biomethaneRoutes.PRODUCER.ENERGY,
        t(
          "<CustomLink>{{page}}</CustomLink> : veuillez renseigner les différents champs de la page. ",
          {
            page: t("Energie"),
          }
        ),
        onPageClick
      )
    if (energyCount === 0) return null
    return generateTranslatedMessage(
      t("Energie"),
      energyCount,
      biomethaneRoutes.PRODUCER.ENERGY,
      t(
        "<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>.",
        {
          count: energyCount,
          page: t("Energie"),
        }
      ),
      onPageClick
    )
  }, [
    energyCount,
    biomethaneRoutes.PRODUCER.ENERGY,
    onPageClick,
    t,
    hasEnergyObject,
  ])

  const supplyPlanErrorMessage = useMemo(() => {
    // Only show the error if there is no supply input filled
    if (hasAtLeastOneSupplyInput) {
      return null
    }

    return (
      <span>
        <Trans
          defaults="<CustomLink>Plan d'approvisionnement</CustomLink> : veuillez renseigner au moins un intrant pour valider votre déclaration annuelle"
          components={{
            CustomLink: (
              // @ts-ignore children is propagated to the button by i18next
              <Button
                customPriority="link"
                linkProps={{
                  to: biomethaneRoutes.PRODUCER.SUPPLY_PLAN,
                  onClick: () =>
                    onPageClick?.(biomethaneRoutes.PRODUCER.SUPPLY_PLAN),
                }}
              />
            ),
          }}
          t={t}
        />
      </span>
    )
  }, [
    t,
    hasAtLeastOneSupplyInput,
    biomethaneRoutes.PRODUCER.SUPPLY_PLAN,
    onPageClick,
  ])

  const errorMessage = useMemo(() => {
    // Filter out null values (when supplyPlanErrorMessage is null)
    const messages = [
      supplyPlanErrorMessage,
      digestateMessage,
      energyMessage,
    ].filter((msg) => msg !== null)
    return messages
  }, [digestateMessage, energyMessage, supplyPlanErrorMessage])

  return { errorMessage, digestateCount, energyCount, hasAtLeastOneSupplyInput }
}
