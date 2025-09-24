import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { apiTypes } from "common/services/api-fetch.types"
import { useUser } from "common/hooks/user"

type ChargePointsParams = Pick<
  apiTypes["NavStats"],
  "charge_point_registration_pending" | "metering_reading_pending" | "audits"
>

export const useChargePoints = (params?: ChargePointsParams) => {
  const { isCPO, isAuditor, isAdmin, hasAdminRight } = useEntity()
  const { isMTEDGEC } = useUser()
  const { t } = useTranslation()
  const routes = useRoutes()

  const chargePoints: MenuSection = {
    title: t("Points de recharge"),
    condition: isCPO,
    children: [
      {
        path: routes.ELEC().CHARGE_POINTS.PENDING,
        title: t("Inscription"),

        icon: "ri-file-text-line",
        iconActive: "ri-file-text-fill",
      },
      {
        path: routes.ELEC().CHARGE_POINTS.METER_READINGS,
        title: t("Relevés trimestriels"),
        icon: "ri-calendar-check-line",
        iconActive: "ri-calendar-check-fill",
      },
      {
        path: routes.ELEC().CHARGE_POINTS.QUALICHARGE,
        title: t("Données Qualicharge"),
        condition: isMTEDGEC,
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
      {
        path: routes.ELEC().CHARGE_POINTS.LIST,
        title: t("Point de recharge"),
        icon: "ri-building-4-line",
        iconActive: "ri-building-4-fill",
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
        additionalInfo: params?.audits,
        icon: "ri-building-4-line",
        iconActive: "ri-building-4-fill",
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
        additionalInfo: params?.charge_point_registration_pending,
        icon: "ri-clipboard-line",
        iconActive: "ri-clipboard-fill",
      },
      {
        path: routes.ELEC_ADMIN().CHARGE_POINTS.METER_READINGS,
        additionalInfo: params?.metering_reading_pending,
        title: t("Relevés"),
        icon: "ri-todo-line",
        iconActive: "ri-todo-fill",
      },
      {
        path: routes.ELEC().CHARGE_POINTS.QUALICHARGE,
        title: t("Données Qualicharge"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
    ],
  }

  return [chargePoints, chargePointsAuditor, chargePointsAdmin]
}
