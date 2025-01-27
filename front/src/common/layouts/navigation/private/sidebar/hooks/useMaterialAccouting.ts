import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"

export const useMaterialAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const { isIndustry, isPowerOrHeatProducer } = useEntity()
  const section: MenuSection = {
    title: t("Comptabilité"),
    condition: isIndustry || isPowerOrHeatProducer,
    children: [
      {
        path: routes.MATERIAL_ACCOUNTING.BALANCE,
        title: t("Comptabilité matière"),
      },
    ],
  }

  return section
}
