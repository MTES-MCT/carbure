/**
 * Builds i18n messages (JSX) for settings missing fields only:
 * Contrat, Site de production, Site d'injection.
 * Used by MissingFieldsSettings on the settings layout.
 */
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useRoutes } from "common/hooks/routes"
import { useMissingFieldCounts } from "./use-missing-fields-helpers"
import {
  generateNoObjectMessage,
  generateTranslatedMessage,
} from "../missing-fields-message.utils"

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

  const contractMessage = useMemo(() => {
    if (!hasContractObject)
      return generateNoObjectMessage(
        t("Contrat"),
        settingsBiomethaneRoutes.CONTRACT,
        t(
          "<CustomLink>{{page}}</CustomLink> : veuillez renseigner les différents champs de la page.",
          { page: t("Contrat") }
        ),
        onPageClick
      )
    if (contractCount === 0) return null
    return generateTranslatedMessage(
      t("Contrat"),
      contractCount,
      settingsBiomethaneRoutes.CONTRACT,
      t(
        "<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>.",
        { count: contractCount, page: t("Contrat") }
      ),
      onPageClick
    )
  }, [
    contractCount,
    settingsBiomethaneRoutes.CONTRACT,
    onPageClick,
    t,
    hasContractObject,
  ])

  const productionMessage = useMemo(() => {
    if (!hasProductionUnitObject)
      return generateNoObjectMessage(
        t("Site de production"),
        settingsBiomethaneRoutes.PRODUCTION,
        t(
          "<CustomLink>{{page}}</CustomLink> : veuillez renseigner les différents champs de la page.",
          { page: t("Site de production") }
        ),
        onPageClick
      )
    if (productionUnitCount === 0) return null
    return generateTranslatedMessage(
      t("Site de production"),
      productionUnitCount,
      settingsBiomethaneRoutes.PRODUCTION,
      t(
        "<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>.",
        {
          count: productionUnitCount,
          page: t("Site de production"),
        }
      ),
      onPageClick
    )
  }, [
    productionUnitCount,
    settingsBiomethaneRoutes.PRODUCTION,
    onPageClick,
    t,
    hasProductionUnitObject,
  ])

  const injectionMessage = useMemo(() => {
    if (!hasInjectionObject)
      return generateNoObjectMessage(
        t("Site d'injection"),
        settingsBiomethaneRoutes.INJECTION,
        t(
          "<CustomLink>{{page}}</CustomLink> : veuillez renseigner les différents champs de la page.",
          { page: t("Site d'injection") }
        ),
        onPageClick
      )
    if (injectionCount === 0) return null
    return generateTranslatedMessage(
      t("Site d'injection"),
      injectionCount,
      settingsBiomethaneRoutes.INJECTION,
      t(
        "<CustomLink>{{page}}</CustomLink> : il y a <strong>{{count}} champs manquants</strong>.",
        { count: injectionCount, page: t("Site d'injection") }
      ),
      onPageClick
    )
  }, [
    injectionCount,
    settingsBiomethaneRoutes.INJECTION,
    onPageClick,
    t,
    hasInjectionObject,
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
