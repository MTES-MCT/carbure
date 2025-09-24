import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import useEntity from "common/hooks/entity"

export const useBiomethane = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const { isBiomethaneProducer } = useEntity()

  const biomethane: MenuSection = {
    title: t("Déclarations"),
    condition: isBiomethaneProducer,
    children: [
      {
        path: routes.BIOMETHANE().SUPPLY_PLAN,
        title: t("Approvisionnement"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
      {
        path: routes.BIOMETHANE().DIGESTATE,
        title: t("Digestat"),
        icon: "ri-contrast-drop-line",
        iconActive: "ri-contrast-drop-fill",
      },
      {
        path: routes.BIOMETHANE().ENERGY,
        title: t("Énergie"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
      },
    ],
  }

  return biomethane
}
