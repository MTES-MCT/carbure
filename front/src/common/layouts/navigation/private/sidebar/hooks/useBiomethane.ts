import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import useEntity from "common/hooks/entity"
import { useLocation } from "react-router-dom"
import { useBiomethanePermissions } from "biomethane/hooks/use-biomethane-permissions"
import { useBiomethaneBusinessRules } from "biomethane/hooks/use-biomethane-business-rules"

const currentYear = new Date().getFullYear()

export const useBiomethane = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const loc = useLocation()
  const { isBiomethaneProducer } = useEntity()
  const { canAccessAdmin, canAccessSupplyPlanAdmin } =
    useBiomethanePermissions()

  const { shouldFillDigestate } = useBiomethaneBusinessRules()

  const routesDeclaration = ["digestate", "energy", "supply-plan"]
  const currentRouteIsDeclaration = routesDeclaration.some((route) =>
    loc.pathname.includes(route)
  )

  // When we are not in the declaration pages, we don't need to pass the year to the routes
  const year = currentRouteIsDeclaration ? currentYear - 1 : undefined

  const biomethaneProducerMenu: MenuSection = {
    title: t("Déclarations"),
    condition: isBiomethaneProducer,
    children: [
      {
        path: routes.BIOMETHANE(year).PRODUCER.SUPPLY_PLAN,
        title: t("Approvisionnement"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
      {
        path: routes.BIOMETHANE(year).PRODUCER.DIGESTATE,
        title: t("Digestat"),
        icon: "ri-contrast-drop-line",
        iconActive: "ri-contrast-drop-fill",
        condition: shouldFillDigestate,
      },
      {
        path: routes.BIOMETHANE(year).PRODUCER.ENERGY,
        title: t("Énergie"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
      },
    ],
  }

  const biomethaneAdminMenu: MenuSection = {
    title: t("Biométhane"),
    condition: canAccessAdmin,
    children: [
      {
        path: routes.BIOMETHANE().ADMIN.DASHBOARD,
        title: t("Tableau de bord"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
      {
        path: routes.BIOMETHANE().ADMIN.SUPPLY_INPUTS,
        title: t("Intrants"),
        icon: "ri-leaf-line",
        iconActive: "ri-leaf-fill",
        condition: canAccessSupplyPlanAdmin,
      },
      {
        path: routes.BIOMETHANE().ADMIN.DECLARATIONS,
        title: t("Déclarations"),
        icon: "ri-file-text-line",
        iconActive: "ri-file-text-fill",
      },
    ],
  }

  return [biomethaneProducerMenu, biomethaneAdminMenu]
}
