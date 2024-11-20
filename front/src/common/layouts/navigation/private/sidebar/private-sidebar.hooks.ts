import useEntity from "carbure/hooks/entity"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  BuildingFill,
  BuildingLine,
  CalendarCheckFill,
  CalendarCheckLine,
  ClipboardFill,
  ClipboardLine,
  ContrastDropFill,
  ContrastDropLine,
  EyeFill,
  EyeLine,
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
    isOperator,
    has_saf,
    isAirline,
    // isProducer,
  } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels = useBiofuels()

  const elec = useElec()

  const chargePoints = useChargePoints()
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
        path: routes.SAF().TICKETS_ASSIGNED,
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

  return [biofuels, ...elec, ...chargePoints, saf]
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

const useBiofuels = () => {
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
    title: t("Lots de biocarburants"),
    condition: isAuditor || isAdmin,
    children: [
      {
        path: routes.BIOFUELS_CONTROLS().ALERTS,
        title: t("Signalements"),
        icon: EyeLine,
        iconActive: EyeFill,
      },
      {
        path: routes.BIOFUELS_CONTROLS().LOTS,
        title: t("Lots"),
        icon: ClipboardLine,
        iconActive: ClipboardFill,
      },
      {
        path: routes.BIOFUELS_CONTROLS().STOCKS,
        title: t("En stock"),
        icon: StackLine,
        iconActive: StackFill,
      },
    ],
  }

  return isAuditor || isAdmin ? biofuelsControls : biofuels
}

const useElec = () => {
  const { has_elec, isOperator, isCPO, isAdmin, hasAdminRight } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

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

  const elecAdmin: MenuSection = {
    ...elec,
    condition: isAdmin || hasAdminRight("ELEC"),
    children: [
      {
        path: routes.ELEC_ADMIN().PROVISION,
        title: t("Certificats de fourniture"),
      },
      {
        path: routes.ELEC_ADMIN().TRANSFER,
        title: t("Energie cédée"),
      },
    ],
  }
  return [elec, elecAdmin]
}

const useChargePoints = () => {
  const { isCPO, isAuditor, isAdmin, hasAdminRight } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

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

  const chargePointsAuditor: MenuSection = {
    ...chargePoints,
    condition: isAuditor,
    children: [
      {
        path: routes.ELEC_AUDITOR(),
        title: t("Point de recharge"),
        icon: BuildingLine,
        iconActive: BuildingFill,
      },
    ],
  }

  const chargePointsAdmin: MenuSection = {
    ...chargePoints,
    condition: isAdmin || hasAdminRight("ELEC"),
    children: [
      {
        path: routes.ELEC_ADMIN().CHARGE_POINTS.PENDING,
        title: t("Inscription"),
      },
      {
        path: routes.ELEC_ADMIN().CHARGE_POINTS.METER_READINGS,
        title: t("Relevés trimestriels"),
      },
    ],
  }

  return [chargePoints, chargePointsAuditor, chargePointsAdmin]
}
