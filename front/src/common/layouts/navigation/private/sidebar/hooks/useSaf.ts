import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  ContrastDropFill,
  ContrastDropLine,
} from "common/components/icon/icon"
import { apiTypes } from "common/services/api-fetch.types"

type SafParams = Pick<apiTypes["NavStats"], "tickets">

export const useSaf = (params?: SafParams) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()

  const { isAirline, isSafTrader, isAdmin } = entity
  const isSafOperator = entity.isOperator && entity.has_saf
  const isSafAdmin = entity.isExternal && entity.hasAdminRight("AIRLINE")

  const saf: MenuSection = {
    title: t("Aviation"),
    condition:
      isAirline || isSafOperator || isSafTrader || isAdmin || isSafAdmin,
    children: [
      {
        path: routes.SAF().TICKET_SOURCES,
        title: t("Volumes SAF"),
        icon: ContrastDropLine,
        iconActive: ContrastDropFill,
        condition: !isAirline,
      },
      {
        path: routes.SAF().TICKETS_ASSIGNED,
        title: t("Tickets affectés"),
        icon: ArrowGoForwardLine,
        condition: !isAirline,
      },
      {
        path: routes.SAF().TICKETS_RECEIVED,
        title: t("Tickets reçus"),
        icon: ArrowGoBackLine,
        additionalInfo: params?.tickets,
        condition: isAirline || isSafOperator || isSafTrader,
      },
    ],
  }

  return saf
}
