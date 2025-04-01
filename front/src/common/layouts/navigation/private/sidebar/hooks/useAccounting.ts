import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import {
  BarChartFill,
  BarChartLine,
  HomeFill,
  HomeLine,
} from "common/components/icon"
import { useUser } from "common/hooks/user"
import useEntity from "common/hooks/entity"

export const useAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const user = useUser()
  const { isProducer, isOperator, isPowerOrHeatProducer, is_tiruert_liable } =
    useEntity()

  const userIsMTEDGEC = user?.rights.find(
    (right) => right.entity.name === "MTE - DGEC"
  )
  console.log("is ", is_tiruert_liable)
  const section: MenuSection = {
    title: t("Comptabilité"),
    condition:
      !!userIsMTEDGEC && (isProducer || isOperator || isPowerOrHeatProducer),
    children: [
      {
        path: routes.ACCOUNTING.OPERATIONS,
        title: t("Comptabilité"),
        icon: BarChartLine,
        iconActive: BarChartFill,
      },
      {
        path: routes.ACCOUNTING.TENEUR,
        title: t("Objectifs annuels"),
        icon: HomeLine,
        iconActive: HomeFill,
        condition: is_tiruert_liable,
      },
    ],
  }

  return section
}
