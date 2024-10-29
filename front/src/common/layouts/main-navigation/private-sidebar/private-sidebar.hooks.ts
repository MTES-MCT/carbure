import { fr } from "@codegouvfr/react-dsfr"
import useEntity from "carbure/hooks/entity"
import { SurveyLine } from "common/components/icon/icon"
import { useRoutes } from "common/hooks/routes"
import { ReactNode } from "react"
import { useTranslation } from "react-i18next"

type MenuItem = {
  title: string
  condition?: boolean
  children: MenuSection[]
}

type MenuSection = Omit<MenuItem, "children"> & {
  icon?: React.ElementType
  path: string
  additionalInfo?: string | number
}

export const usePrivateSidebar = () => {
  const {
    isAdmin,
    isAuditor,
    isIndustry,
    isOperator,
    isPowerOrHeatProducer,
    has_saf,
    isAirline,
    isProducer,
    isCPO,
    has_elec,
  } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const biofuels: MenuItem = {
    title: t("Lot de biocarburants"),
    // condition: isIndustry || isPowerOrHeatProducer,
    condition: true,
    children: [
      {
        path: routes.BIOFUELS().DRAFT,
        title: t("Brouillons"),
        icon: SurveyLine,
      },
      {
        path: routes.BIOFUELS().RECEIVED,
        title: t("Reçus"),
        additionalInfo: "12",
        icon: SurveyLine,
      },
    ],
  }

  return [biofuels].filter((category) =>
    category.condition
      ? {
          ...category,
          children: category.children.filter((child) => child.condition),
        }
      : category
  )
}
