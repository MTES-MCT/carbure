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
  const { has_saf, isOperator, isAirline } = useEntity()

  const saf: MenuSection = {
    title: t("Aviation"),
    condition: (has_saf && isOperator) || isAirline,
    children: [
      {
        path: routes.SAF().TICKET_SOURCES,
        title: t("Volumes SAF"),
        icon: ContrastDropLine,
        iconActive: ContrastDropFill,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS_ASSIGNED,
        title: t("Tickets affectés"),
        icon: ArrowGoForwardLine,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS_RECEIVED,
        title: t("Tickets reçus"),
        icon: ArrowGoBackLine,
        condition: has_saf && isOperator,
      },
      {
        path: routes.SAF().TICKETS_PENDING,
        title: t("Tickets en attente"),
        additionalInfo: params?.tickets,
        icon: ArrowGoBackLine,
        condition: isAirline,
      },
      {
        path: routes.SAF().TICKETS_ACCEPTED,
        title: t("Tickets acceptés"),
        icon: ArrowGoForwardLine,
        condition: isAirline,
      },
    ],
  }

  return saf
}
