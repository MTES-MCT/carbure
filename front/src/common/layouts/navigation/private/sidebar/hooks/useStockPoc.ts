import useEntity from "common/hooks/entity"
import { ROUTE_URLS } from "common/utils/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"

export const useStockPoc = (): MenuSection => {
  const { t } = useTranslation()
  const entity = useEntity()

  return {
    title: t("Stock POC"),
    children: [
      {
        path: ROUTE_URLS.STOCK_POC(entity.id),
        title: t("Arborescence des actions"),
        icon: "ri-stack-line",
        iconActive: "ri-stack-line",
      },
    ],
  }
}
