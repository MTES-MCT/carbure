import { useTranslation } from "react-i18next"
import { MenuSection } from "../private-sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "carbure/hooks/entity"
import {
  FileTextFill,
  FileTextLine,
  HotelFill,
  HotelLine,
} from "common/components/icon"

export const useDoubleCount = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, hasAdminRight } = useEntity()

  const doubleCount: MenuSection = {
    title: t("Double-comptage"),
    condition: isAdmin || hasAdminRight("DCA"),
    children: [
      {
        path: routes.ADMIN().DOUBLE_COUNT.APPLICATIONS,
        title: t("En attente"),
        icon: FileTextLine,
        iconActive: FileTextFill,
      },
      {
        path: routes.ADMIN().DOUBLE_COUNT.AGREEMENTS,
        title: t("Agréments actifs"),
        icon: HotelLine,
        iconActive: HotelFill,
      },
    ],
  }

  return doubleCount
}
