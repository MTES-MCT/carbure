import { useRoutes } from "common/hooks/routes"
import { MenuSection } from "../sidebar.types"
import { useTranslation } from "react-i18next"
import { createIcon } from "common/components/icon"
import { useUser } from "common/hooks/user"
import useEntity from "common/hooks/entity"

export const useAccounting = () => {
  const routes = useRoutes()
  const { t } = useTranslation()
  const user = useUser()
  const { is_tiruert_liable, accise_number } = useEntity()

  const userIsMTEDGEC = user?.rights.find(
    (right) => right.entity.name === "MTE - DGEC"
  )

  const section: MenuSection = {
    title: t("Comptabilité"),
    condition: Boolean(userIsMTEDGEC) && accise_number !== "",
    children: [
      {
        path: routes.ACCOUNTING.BALANCES,
        title: t("Soldes"),
        icon: createIcon({ name: "ri-bank-line" }),
        iconActive: createIcon({ name: "ri-bank-fill" }),
      },
      {
        path: routes.ACCOUNTING.OPERATIONS,
        title: t("Comptabilité"),
        icon: createIcon({ name: "ri-bar-chart-2-line" }),
        iconActive: createIcon({ name: "ri-bar-chart-2-fill" }),
      },
      {
        path: routes.ACCOUNTING.TENEUR,
        title: t("Objectifs annuels"),
        icon: createIcon({ name: "ri-flashlight-line" }),
        iconActive: createIcon({ name: "ri-flashlight-fill" }),
        condition: is_tiruert_liable,
      },
    ],
  }

  return section
}
