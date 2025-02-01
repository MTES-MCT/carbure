import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "carbure/hooks/entity"
import { BookFill, BookLine } from "common/components/icon"
import { apiTypes } from "common/services/api-fetch.types"
import { ExtAdminPagesEnum } from "api-schema"

type AdminParams = Pick<apiTypes["NavStats"], "total_pending_action_for_admin">

// To add when company page will be implemented
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
export const useAdmin = (params?: AdminParams) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, hasAdminRight, isExternal, ext_admin_pages } = useEntity()
  const isAdminDC = isExternal && hasAdminRight("DCA")
  const isAdminAirline = isExternal && hasAdminRight("AIRLINE")
  const isElecAdmin = isExternal && hasAdminRight("ELEC")

  const admin: MenuSection = {
    title: t("Admin"),
    condition:
      isAdmin || ext_admin_pages.includes(ExtAdminPagesEnum.TRANSFERRED_ELEC),
    children: [
      {
        path: routes.ADMIN().COMPANIES,
        title: t("Sociétés"),
        condition:
          isAdmin ||
          isAdminAirline ||
          isElecAdmin ||
          isAdminDC ||
          ext_admin_pages.includes(ExtAdminPagesEnum.TRANSFERRED_ELEC),
        icon: BookLine,
        iconActive: BookFill,
      },
    ],
  }

  return admin
}
