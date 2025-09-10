import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import useEntity from "common/hooks/entity"
import { createIcon } from "common/components/icon"

export const useBiomethane = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const { isBiomethaneProducer } = useEntity()

  const biomethane: MenuSection = {
    title: t("Déclarations"),
    condition: isBiomethaneProducer,
    children: [
      {
        path: routes.BIOMETHANE().DIGESTATE,
        title: t("Digestat"),
        icon: createIcon({ name: "ri-home-4-line" }),
        iconActive: createIcon({ name: "ri-home-4-fill" }),
      },
      {
        path: routes.BIOMETHANE().ENERGY,
        title: t("Énergie"),
        icon: createIcon({ name: "ri-flashlight-line" }),
        iconActive: createIcon({ name: "ri-flashlight-fill" }),
      },
    ],
  }

  return biomethane
}
