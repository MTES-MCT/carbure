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
    isCPO,
  } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels = useBiofuels()

  const elec = useElec()

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

const useBiofuels = () => {
  const { isAuditor, isIndustry, isPowerOrHeatProducer, has_stocks } =
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

  const biofuelsAuditor: MenuSection = {
    title: t("Lots de biocarburants"),
    condition: isAuditor,
    children: [
      {
        path: routes.BIOFUELS_AUDITOR().ALERTS,
        title: t("Signalements"),
        icon: EyeLine,
        iconActive: EyeFill,
      },
      {
        path: routes.BIOFUELS_AUDITOR().LOTS,
        title: t("Lots"),
        icon: ClipboardLine,
        iconActive: ClipboardFill,
      },
      {
        path: routes.BIOFUELS_AUDITOR().STOCKS,
        title: t("En stock"),
        icon: StackLine,
        iconActive: StackFill,
      },
    ],
  }

  return isAuditor ? biofuelsAuditor : biofuels
}

const useElec = () => {
  const { has_elec, isOperator, isCPO, isAuditor } = useEntity()
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

  const elecAuditor: MenuSection = {
    ...elec,
    condition: isAuditor,
    children: [
      {
        path: routes.ELEC_AUDITOR(),
        title: t("Certificats"),
        icon: FileTextLine,
        iconActive: FileTextFill,
      },
    ],
  }

  return isAuditor ? elecAuditor : elec
}
