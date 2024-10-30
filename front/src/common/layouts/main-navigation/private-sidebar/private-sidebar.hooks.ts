import useEntity from "carbure/hooks/entity"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  ContrastDropFill,
  ContrastDropLine,
  FileTextFill,
  FileTextLine,
  InboxArchiveFill,
  InboxArchiveLine,
  SendPlaneFill,
  SendPlaneLine,
  StackFill,
  StackLine,
  SurveyFill,
  SurveyLine,
} from "common/components/icon/icon"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "./private-sidebar.types"

export const usePrivateSidebar = () => {
  const {
    isAdmin,
    isAuditor,
    isIndustry,
    isOperator,
    isPowerOrHeatProducer,
    has_saf,
    isAirline,
    isProducer,
    isCPO,
    has_elec,
  } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels: MenuSection = {
    title: t("Lot de biocarburants"),
    // condition: isIndustry || isPowerOrHeatProducer,
    condition: true,
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
      },
      {
        path: routes.BIOFUELS().SENT,
        title: t("Envoyés"),
        icon: SendPlaneLine,
        iconActive: SendPlaneFill,
      },
    ],
  }

  const elec: MenuSection = {
    title: t("Certificats d'électricité"),
    condition: true,
    children: [
      {
        path: routes.ELEC_CERTIFICATES,
        title: t("Certificats"),
        icon: FileTextLine,
        iconActive: FileTextFill,
      },
    ],
  }

  const saf: MenuSection = {
    title: t("Aviation"),
    condition: true,
    children: [
      {
        path: routes.SAF().TICKET_SOURCES,
        title: t("Volumes SAF"),
        icon: ContrastDropLine,
        iconActive: ContrastDropFill,
      },
      {
        path: routes.SAF().TICKETS_AFFECTED,
        title: t("Tickets affectés"),
        icon: ArrowGoForwardLine,
      },
      {
        path: routes.SAF().TICKETS_RECEIVED,
        title: t("Tickets reçus"),
        icon: ArrowGoBackLine,
      },
    ],
  }

  return [biofuels, elec, saf].filter((category) =>
    category.condition
      ? {
          ...category,
          children: category.children.filter((child) => child.condition),
        }
      : category
  )
}
