import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"

export const useHydrogen = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const h2Routes = routes.HYDROGEN()
  const { isHRS } = useEntity()

  const menu: MenuSection[] = [
    {
      title: t("Unités consommatrices"),
      condition: isHRS,
      children: [
        {
          path: h2Routes.STATIONS,
          title: t("Mes stations"),
          icon: "ri-gas-station-line",
          iconActive: "ri-gas-station-fill",
        },
      ],
    },
    {
      title: t("Lots d'hydrogène"),
      condition: isHRS,
      children: [
        {
          path: h2Routes.LOTS,
          title: t("Lots"),
          icon: "ri-inbox-archive-line",
          iconActive: "ri-inbox-archive-fill",
        },
        {
          path: h2Routes.CERTIFICATES,
          title: t("Certificats"),
          icon: "ri-send-plane-line",
          iconActive: "ri-send-plane-fill",
        },
      ],
    },
  ]

  return menu
}
