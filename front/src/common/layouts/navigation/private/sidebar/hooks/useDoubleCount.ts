import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import { apiTypes } from "common/services/api-fetch.types"

type DoubleCountParams = Pick<
  apiTypes["NavStats"],
  "doublecount_agreement_pending"
>

export const useDoubleCount = (params?: DoubleCountParams) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isAdmin, hasAdminRight, isProducer } = useEntity()

  const doubleCount: MenuSection = {
    title: t("Double-comptage"),
    condition: isProducer,
    children: [
      {
        path: routes.DOUBLE_COUNTING().AGREEMENTS,
        title: t("Agréments"),
        icon: "ri-home-4-line",
        iconActive: "ri-home-4-fill",
      },
    ],
  }

  const doubleCountAdmin: MenuSection = {
    title: t("Double-comptage"),
    condition: isAdmin || hasAdminRight("DCA"),
    children: [
      {
        path: routes.ADMIN().DOUBLE_COUNT.APPLICATIONS,
        title: t("En attente"),
        additionalInfo: params?.doublecount_agreement_pending,
        icon: "ri-file-text-line",
        iconActive: "ri-file-text-fill",
      },
      {
        path: routes.ADMIN().DOUBLE_COUNT.AGREEMENTS,
        title: t("Agréments actifs"),
        icon: "ri-file-download-line",
        iconActive: "ri-file-download-fill",
      },
    ],
  }

  return [doubleCount, doubleCountAdmin]
}
