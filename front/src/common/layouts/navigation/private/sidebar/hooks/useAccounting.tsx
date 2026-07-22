import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useAccountingPermissions } from "accounting/hooks/use-accounting-permissions"

export const useAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const permissions = useAccountingPermissions()
  const { adminPermissions } = permissions

  const section: MenuSection = {
    title: t("Comptabilité"),
    badge: <Badge severity="info">BETA</Badge>,
    condition: permissions.canAccessModule,
    children: [
      {
        path: routes.ACCOUNTING.BALANCES.ROOT,
        title: t("Soldes"),
        icon: "ri-bank-line",
        iconActive: "ri-bank-fill",
        condition: permissions.canAccessBalances,
      },
      {
        path: adminPermissions.canAccessAdmin
          ? routes.ACCOUNTING.ADMIN.OPERATIONS
          : routes.ACCOUNTING.OPERATIONS.ROOT,
        title: t("Opérations"),
        icon: "ri-bar-chart-2-line",
        iconActive: "ri-bar-chart-2-fill",
        condition: permissions.canAccessOperations,
      },
      {
        path: adminPermissions.canAccessAdmin
          ? routes.ACCOUNTING.ADMIN.OBJECTIVES
          : routes.ACCOUNTING.TENEUR.ROOT,
        title: t("Objectifs annuels"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
        condition: permissions.canAccessObjectives,
      },
    ],
  }

  return section
}
