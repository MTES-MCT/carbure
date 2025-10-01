import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { apiTypes } from "common/services/api-fetch.types"

type BiofuelsParams = Pick<
  apiTypes["NavStats"],
  "pending_draft_lots" | "in_pending_lots"
>

export const useBiofuels = (params?: BiofuelsParams) => {
  const { isAuditor, isIndustry, isPowerOrHeatProducer, has_stocks, isAdmin } =
    useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels: MenuSection = {
    title: t("Lots de biocarburants"),
    condition: isIndustry || isPowerOrHeatProducer,
    children: [
      {
        path: routes.BIOFUELS().DRAFT,
        title: t("Brouillons"),
        additionalInfo: params?.pending_draft_lots,
        icon: "fr-icon-survey-line",
        iconActive: "fr-icon-survey-fill",
      },
      {
        path: routes.BIOFUELS().RECEIVED,
        title: t("Reçus"),
        additionalInfo: params?.in_pending_lots,
        icon: "ri-inbox-archive-line",
        iconActive: "ri-inbox-archive-fill",
      },
      {
        path: routes.BIOFUELS().STOCKS,
        title: t("En stock"),
        icon: "ri-stack-line",
        iconActive: "ri-stack-line",
        condition: has_stocks,
      },
      {
        path: routes.BIOFUELS().SENT,
        title: t("Envoyés"),
        icon: "ri-send-plane-line",
        iconActive: "ri-send-plane-fill",
      },
    ],
  }

  const biofuelsControls: MenuSection = {
    ...biofuels,
    condition: isAuditor || isAdmin,
    children: [
      {
        path: routes.BIOFUELS_CONTROLS().ALERTS,
        title: t("Signalements"),
        icon: "fr-icon-survey-line",
        iconActive: "fr-icon-survey-fill",
      },
      {
        path: routes.BIOFUELS_CONTROLS().LOTS,
        title: t("Lots"),
        icon: "ri-inbox-archive-line",
        iconActive: "ri-inbox-archive-fill",
      },
      {
        path: routes.BIOFUELS_CONTROLS().STOCKS,
        title: t("En stock"),
        icon: "ri-stack-line",
        iconActive: "ri-stack-line",
      },
    ],
  }

  return [biofuelsControls, biofuels]
}
