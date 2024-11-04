import useEntity from "carbure/hooks/entity"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  BuildingFill,
  BuildingLine,
  CalendarCheckFill,
  CalendarCheckLine,
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
    // isAdmin,
    // isAuditor,
    isIndustry,
    isOperator,
    isPowerOrHeatProducer,
    has_saf,
    isAirline,
    // isProducer,
    isCPO,
    has_elec,
  } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels: MenuSection = {
    title: t("Lot de biocarburants"),
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
    condition: (has_elec && isOperator) || isCPO,
    children: [
      {
        path: routes.ELEC().CERTIFICATES,
        title: t("Certificats"),
        icon: FileTextLine,
        iconActive: FileTextFill,
        condition: has_elec && isOperator,
      },
      {
        path: routes.ELEC().PROVISIONNED_ENERGY,
        title: t("Énergie disponible"),
        icon: ArrowGoBackLine,
        condition: isCPO,
      },
      {
        path: routes.ELEC().TRANSFERRED_ENERGY,
        title: t("Énergie cédée"),
        icon: ArrowGoForwardLine,
        condition: isCPO,
      },
    ],
  }

  const chargePoints: MenuSection = {
    title: t("Point de recharge"),
    condition: isCPO,
    children: [
      {
        path: routes.ELEC().CHARGE_POINTS.PENDING,
        title: t("Inscription"),
        icon: FileTextLine,
        iconActive: FileTextFill,
      },
      {
        path: routes.ELEC().CHARGE_POINTS.METER_READINGS,
        title: t("Relevés trimestriels"),
        icon: CalendarCheckLine,
        iconActive: CalendarCheckFill,
      },
      {
        path: routes.ELEC().CHARGE_POINTS.LIST,
        title: t("Point de recharge"),
        icon: BuildingLine,
        iconActive: BuildingFill,
      },
    ],
  }

  const saf: MenuSection = {
    title: t("Aviation"),
    condition: (has_saf && isOperator) || isAirline,
    children: [
      {
        path: routes.SAF().TICKET_SOURCES,
        title: t("Volumes SAF"),
        icon: ContrastDropLine,
        iconActive: ContrastDropFill,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS,
        title: t("Tickets affectés"),
        icon: ArrowGoForwardLine,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS_RECEIVED,
        title: t("Tickets reçus"),
        icon: ArrowGoBackLine,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS_PENDING,
        title: t("Tickets en attente"),
        icon: ArrowGoBackLine,
        condition: isAirline,
      },
      {
        path: routes.SAF().TICKETS_ACCEPTED,
        title: t("Tickets acceptés"),
        icon: ArrowGoForwardLine,
        condition: isAirline,
      },
    ],
  }

  return [biofuels, elec, chargePoints, saf]
    .filter(
      (category) =>
        category.condition === undefined || category.condition === true
    )
    .map((category) => ({
      ...category,
      children: category.children.filter(
        (child) => child.condition === undefined || child.condition === true
      ),
    }))
}
