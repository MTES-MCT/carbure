import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import useEntity from "common/hooks/entity"
import { getDeclarationInterval } from "biomethane/utils"

// Get the current declaration year for Digestate/Energy
const declarationYear = getDeclarationInterval().year

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
        path: routes.BIOMETHANE(declarationYear).DIGESTATE,
        title: t("Digestat"),
        icon: "ri-contrast-drop-line",
        iconActive: "ri-contrast-drop-fill",
      },
      {
        path: routes.BIOMETHANE(declarationYear).ENERGY,
        title: t("Énergie"),
        icon: "ri-flashlight-line",
        iconActive: "ri-flashlight-fill",
      },
    ],
  }

  return biomethane
}
