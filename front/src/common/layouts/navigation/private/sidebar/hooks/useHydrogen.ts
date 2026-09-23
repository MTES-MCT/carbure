import { useTranslation } from "react-i18next"
import { MenuItem, MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"

export const useHydrogen = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const h2Routes = routes.HYDROGEN()
  const { isHRS } = useEntity()
  const { canAccessAdmin } = useH2Permissions()

  const baseMenu: Record<"lot" | "certificate" | "station", MenuItem> = {
    lot: {
      path: h2Routes.LOTS,
      title: t("Lots"),
      icon: "ri-inbox-archive-line",
      iconActive: "ri-inbox-archive-fill",
    },
    certificate: {
      path: h2Routes.CERTIFICATES,
      title: t("Certificats"),
      icon: "ri-send-plane-line",
      iconActive: "ri-send-plane-fill",
    },
    station: {
      path: h2Routes.STATIONS,
      title: t("Mes stations"),
      icon: "ri-gas-station-line",
      iconActive: "ri-gas-station-fill",
    },
  }

  const menu: MenuSection[] = [
    {
      title: t("Unités consommatrices"),
      condition: isHRS,
      children: [baseMenu.station],
    },
    {
      title: t("Lots d'hydrogène"),
      condition: isHRS,
      children: [baseMenu.lot, baseMenu.certificate],
    },
  ]

  const adminMenu: MenuSection[] = [
    {
      title: t("Hydrogène"),
      children: [
        {
          ...baseMenu.station,
          path: h2Routes.ADMIN.STATIONS,
          title: t("Stations"),
        },
        {
          ...baseMenu.lot,
          path: h2Routes.ADMIN.LOTS,
        },
        {
          ...baseMenu.certificate,
          path: h2Routes.ADMIN.CERTIFICATES,
        },
      ],
    },
  ]

  if (canAccessAdmin) return adminMenu

  return menu
}
