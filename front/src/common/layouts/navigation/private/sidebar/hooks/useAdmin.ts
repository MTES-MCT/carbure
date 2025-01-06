import { useTranslation } from "react-i18next"
import { MenuSection } from "../private-sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "carbure/hooks/entity"
import { DashboardFill, DashboardLine } from "common/components/icon"

export const useAdmin = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin } = useEntity()
  const admin: MenuSection = {
    title: t("Admin"),
    condition: isAdmin,
    children: [
      {
        path: routes.ADMIN().DASHBOARD,
        title: t("Tableau de bord"),
        icon: DashboardLine,
        iconActive: DashboardFill,
      },
    ],
  }

  return admin
}
