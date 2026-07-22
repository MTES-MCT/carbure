import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useAccountingPermissions } from "accounting/hooks/use-accounting-permissions"
import { ACCOUNTING_SIDEBAR_NAV } from "accounting/navigation/sidebar-pages"

const accountingBadge = <Badge severity="info">BETA</Badge>

export const useAccounting = (): MenuSection => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const permissions = useAccountingPermissions()

  const profile = permissions.adminPermissions.canAccessAdmin
    ? "admin"
    : "redevable"

  const currentProfileNavItems = ACCOUNTING_SIDEBAR_NAV[profile]

  return {
    title: t("Comptabilité"),
    badge: accountingBadge,
    condition: permissions.canAccessModule,
    children: currentProfileNavItems.map(
      ({ titleKey, icon, iconActive, path, canAccess }) => ({
        title: t(titleKey),
        icon,
        iconActive,
        path: path(routes.ACCOUNTING),
        condition: canAccess(permissions),
      })
    ),
  }
}
