import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { Badge } from "@codegouvfr/react-dsfr/Badge"

export const useAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()

  const { is_tiruert_liable, accise_number, isAdmin, hasAdminRight } =
    useEntity()

  const section: MenuSection = {
    title: t("Comptabilité"),
    badge: <Badge severity="info">BETA</Badge>,
    condition: accise_number !== "" || isAdmin || hasAdminRight("TIRIB"),
    children: [
      {
        path: routes.ACCOUNTING.BALANCES.ROOT,
        title: t("Soldes"),
        icon: "ri-bank-line",
        iconActive: "ri-bank-fill",
        condition: !isAdmin && !hasAdminRight("TIRIB"),
      },
      {
        path: routes.ACCOUNTING.OPERATIONS.ROOT,
        title: t("Opérations"),
        icon: "ri-bar-chart-2-line",
        iconActive: "ri-bar-chart-2-fill",
        condition: !isAdmin && !hasAdminRight("TIRIB"),
      },
      {
        path: routes.ACCOUNTING.TENEUR,
        title: t("Objectifs annuels"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
        condition: is_tiruert_liable || isAdmin || hasAdminRight("TIRIB"),
      },
    ],
  }

  return section
}
