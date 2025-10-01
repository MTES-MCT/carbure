import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import { apiTypes } from "common/services/api-fetch.types"

type AdminParams = Pick<apiTypes["NavStats"], "total_pending_action_for_admin">

// To add when company page will be implemented
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
export const useAdmin = (params?: AdminParams) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, isExternal } = useEntity()

  const admin: MenuSection = {
    title: t("Admin"),
    condition: isAdmin || isExternal,
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
