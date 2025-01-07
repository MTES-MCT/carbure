import useEntity from "carbure/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../private-sidebar.types"
import {
  InboxArchiveFill,
  InboxArchiveLine,
  SendPlaneFill,
  SendPlaneLine,
  StackFill,
  StackLine,
  SurveyFill,
  SurveyLine,
} from "common/components/icon"

export const useBiofuels = () => {
  const { isAuditor, isIndustry, isPowerOrHeatProducer, has_stocks, isAdmin } =
    useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()
  console.log("has_stocks", has_stocks)
  const biofuels: MenuSection = {
    title: t("Lots de biocarburants"),
    condition: isIndustry || isPowerOrHeatProducer,
    children: [
      {
        path: routes.BIOFUELS().DRAFT,
        title: t("Brouillons"),
        icon: SurveyLine,
        iconActive: SurveyFill,
      },
      {
        path: routes.BIOFUELS().RECEIVED,
        title: t("Reçus"),
        additionalInfo: "12",
        icon: InboxArchiveLine,
        iconActive: InboxArchiveFill,
      },
      {
        path: routes.BIOFUELS().STOCKS,
        title: t("En stock"),
        additionalInfo: "12",
        icon: StackLine,
        iconActive: StackFill,
        condition: has_stocks,
      },
      {
        path: routes.BIOFUELS().SENT,
        title: t("Envoyés"),
        icon: SendPlaneLine,
        iconActive: SendPlaneFill,
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
        icon: SurveyLine,
        iconActive: SurveyFill,
      },
      {
        path: routes.BIOFUELS_CONTROLS().LOTS,
        title: t("Lots"),
        icon: InboxArchiveLine,
        iconActive: InboxArchiveFill,
      },
      {
        path: routes.BIOFUELS_CONTROLS().STOCKS,
        title: t("En stock"),
        icon: StackLine,
        iconActive: StackFill,
      },
    ],
  }

  return [biofuelsControls, biofuels]
}
