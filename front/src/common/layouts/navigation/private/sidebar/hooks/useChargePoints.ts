import useEntity from "carbure/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import {
  BuildingFill,
  BuildingLine,
  CalendarCheckFill,
  CalendarCheckLine,
  ClipboardFill,
  ClipboardLine,
  FileTextFill,
  FileTextLine,
  TodoFill,
  TodoLine,
} from "common/components/icon/icon"

export const useChargePoints = () => {
  const { isCPO, isAuditor, isAdmin, hasAdminRight } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const chargePoints: MenuSection = {
    title: t("Points de recharge"),
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
        title: t("Points de recharge"),
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
        icon: ClipboardLine,
        iconActive: ClipboardFill,
      },
      {
        path: routes.ELEC_ADMIN().CHARGE_POINTS.METER_READINGS,
        title: t("Relevés"),
        icon: TodoLine,
        iconActive: TodoFill,
      },
    ],
  }

  return [chargePoints, chargePointsAuditor, chargePointsAdmin]
}
