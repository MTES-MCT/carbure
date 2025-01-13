import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "carbure/hooks/entity"
import { BookFill, BookLine } from "common/components/icon"

export const useAdmin = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, hasAdminRight, isExternal } = useEntity()
  const isAdminDC = isExternal && hasAdminRight("DCA")
  const isAdminAirline = isExternal && hasAdminRight("AIRLINE")
  const isElecAdmin = isExternal && hasAdminRight("ELEC")

  const admin: MenuSection = {
    title: t("Admin"),
    condition: isAdmin,
    children: [
      {
        path: routes.ADMIN().COMPANIES,
        title: t("Sociétés"),
        condition: isAdmin || isAdminAirline || isElecAdmin || isAdminDC,
        icon: BookLine,
        iconActive: BookFill,
      },
    ],
  }

  return admin
}
