import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { BarChartFill, BarChartLine } from "common/components/icon"

export const useMaterialAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const { isIndustry, isPowerOrHeatProducer } = useEntity()
  const section: MenuSection = {
    title: t("Comptabilité"),
    condition: isIndustry || isPowerOrHeatProducer,
    children: [
      {
        path: routes.MATERIAL_ACCOUNTING.OPERATIONS,
        title: t("Comptabilité"),
        icon: BarChartLine,
        iconActive: BarChartFill,
      },
    ],
  }

  return section
}
