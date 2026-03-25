/**
 * Builds i18n messages (JSX) for declaration missing fields only:
 * Digestat, Énergie, Plan d'approvisionnement.
 * Used by MissingFields on digestate, energy, supply-plan pages.
 */
import { useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { useRoutes } from "common/hooks/routes"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useMissingFieldCounts } from "./use-missing-fields-helpers"
import {
  generateNoObjectMessage,
  generateTranslatedMessage,
} from "../missing-fields-message.utils"

export const useMissingFieldsMessages = ({
  onPageClick,
}: {
  onPageClick?: (page: string) => void
} = {}) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { selectedYear, annualDeclaration } = useAnnualDeclaration()
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
        "<CustomLink>{{page}}</CustomLink> : <strong>{{count}} informations non renseignées</strong>.",
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
        "<CustomLink>{{page}}</CustomLink> : <strong>{{count}} informations non renseignées</strong>.",
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
    if (annualDeclaration?.missing_fields?.supply_plan_valid) {
      return null
    }

    return (
      <span key="supply-plan-error-message">
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
    annualDeclaration?.missing_fields?.supply_plan_valid,
    biomethaneRoutes.PRODUCER.SUPPLY_PLAN,
    onPageClick,
  ])

  const errorMessage = useMemo(() => {
    const messages = [
      supplyPlanErrorMessage,
      digestateMessage,
      energyMessage,
    ].filter((msg) => msg !== null)
    return messages
  }, [digestateMessage, energyMessage, supplyPlanErrorMessage])

  return { errorMessage, digestateCount, energyCount }
}
