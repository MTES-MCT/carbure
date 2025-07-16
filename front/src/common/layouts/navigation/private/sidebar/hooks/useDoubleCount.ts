import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import {
  FileDownloadFill,
  FileDownloadLine,
  FileTextFill,
  FileTextLine,
  HomeFill,
  HomeLine,
} from "common/components/icon"
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
        icon: HomeLine,
        iconActive: HomeFill,
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
        icon: FileTextLine,
        iconActive: FileTextFill,
      },
      {
        path: routes.ADMIN().DOUBLE_COUNT.AGREEMENTS,
        title: t("Agréments actifs"),
        icon: FileDownloadLine,
        iconActive: FileDownloadFill,
      },
    ],
  }

  return [doubleCount, doubleCountAdmin]
}
