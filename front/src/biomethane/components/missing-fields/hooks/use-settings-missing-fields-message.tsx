/**
 * Builds i18n messages (JSX) for settings missing fields only:
 * Contrat, Site de production, Site d'injection.
 * Used by MissingFieldsSettings on the settings layout.
 */
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useRoutes } from "common/hooks/routes"
import { useMissingFieldCounts } from "./use-missing-fields-helpers"
import { generateTranslatedMessage } from "../missing-fields-message.utils"

export const useSettingsMissingFieldsMessages = ({
  onPageClick,
}: {
  onPageClick?: (page: string) => void
} = {}) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const settingsBiomethaneRoutes = routes.SETTINGS.BIOMETHANE
  const {
    contractCount,
    productionUnitCount,
    injectionCount,
    hasContractObject,
    hasProductionUnitObject,
    hasInjectionObject,
  } = useMissingFieldCounts()

  const buildMessage = useCallback(
    (page: string, count: number, route: string) =>
      generateTranslatedMessage(
        page,
        count,
        route,
        t(
          "<CustomLink>{{page}}</CustomLink> : <strong>{{count}} informations non renseignées</strong>.",
          { count, page }
        ),
        onPageClick
      ),
    [t, onPageClick]
  )

  const contractMessage = useMemo(() => {
    if (!hasContractObject || contractCount === 0) return null

    return buildMessage(
      t("Contrat"),
      contractCount,
      settingsBiomethaneRoutes.CONTRACT
    )
  }, [
    contractCount,
    settingsBiomethaneRoutes.CONTRACT,
    t,
    hasContractObject,
    buildMessage,
  ])

  const productionMessage = useMemo(() => {
    if (!hasProductionUnitObject || productionUnitCount === 0) return null
    return buildMessage(
      t("Site de production"),
      productionUnitCount,
      settingsBiomethaneRoutes.PRODUCTION
    )
  }, [
    productionUnitCount,
    settingsBiomethaneRoutes.PRODUCTION,
    t,
    hasProductionUnitObject,
    buildMessage,
  ])

  const injectionMessage = useMemo(() => {
    if (!hasInjectionObject || injectionCount === 0) return null
    return buildMessage(
      t("Site d'injection"),
      injectionCount,
      settingsBiomethaneRoutes.INJECTION
    )
  }, [
    injectionCount,
    settingsBiomethaneRoutes.INJECTION,
    t,
    hasInjectionObject,
    buildMessage,
  ])

  const errorMessage = useMemo(() => {
    const messages = [
      contractMessage,
      productionMessage,
      injectionMessage,
    ].filter((msg) => msg !== null)
    return messages
  }, [contractMessage, productionMessage, injectionMessage])

  return { errorMessage }
}
