import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import { apiTypes } from "common/services/api-fetch.types"
import { ExternalAdminPages } from "common/types"

type AdminParams = Pick<apiTypes["NavStats"], "total_pending_action_for_admin">

// To add when company page will be implemented
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
export const useAdmin = (params?: AdminParams) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, isExternal, hasAdminRight } = useEntity()

  // For now, only external admin ADEME cannot access admin module
  const isAllowedToAccessAdmin =
    isAdmin || (isExternal && !hasAdminRight(ExternalAdminPages.ADEME))

  const admin: MenuSection = {
    title: t("Admin"),
    condition: isAllowedToAccessAdmin,
    children: [
      {
        path: routes.ADMIN().COMPANIES,
        title: t("Sociétés"),
        icon: "ri-book-2-line",
        iconActive: "ri-book-2-fill",
      },
      {
        path: routes.ADMIN().DASHBOARD,
        condition: isAdmin,
        title: t("Tableau de bord"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
    ],
  }

  return admin
}
