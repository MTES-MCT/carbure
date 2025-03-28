import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import { BarChartFill, BarChartLine } from "common/components/icon"
import { useUser } from "common/hooks/user"
import useEntity from "common/hooks/entity"

export const useMaterialAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const user = useUser()
  const { isIndustry, isPowerOrHeatProducer } = useEntity()

  const userIsMTEDGEC = user?.rights.find(
    (right) => right.entity.name === "MTE - DGEC"
  )
  const section: MenuSection = {
    title: t("Comptabilité"),
    condition: !!userIsMTEDGEC && (isIndustry || isPowerOrHeatProducer),
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
