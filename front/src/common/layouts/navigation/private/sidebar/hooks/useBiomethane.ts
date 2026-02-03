import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import useEntity from "common/hooks/entity"
import { useLocation } from "react-router-dom"

const currentYear = new Date().getFullYear()

export const useBiomethane = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const loc = useLocation()
  const { isBiomethaneProducer } = useEntity()

  const routesDeclaration = ["digestate", "energy", "supply-plan"]
  const currentRouteIsDeclaration = routesDeclaration.some((route) =>
    loc.pathname.includes(route)
  )

  // When we are not in the declaration pages, we don't need to pass the year to the routes
  const year = !currentRouteIsDeclaration ? undefined : currentYear - 1

  const biomethane: MenuSection = {
    title: t("Déclarations"),
    condition: isBiomethaneProducer,
    children: [
      {
        path: routes.BIOMETHANE(year).SUPPLY_PLAN,
        title: t("Approvisionnement"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
      {
        path: routes.BIOMETHANE(year).DIGESTATE,
        title: t("Digestat"),
        icon: "ri-contrast-drop-line",
        iconActive: "ri-contrast-drop-fill",
      },
      {
        path: routes.BIOMETHANE(year).ENERGY,
        title: t("Énergie"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
      },
    ],
  }

  return biomethane
}
