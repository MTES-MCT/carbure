import useEntity from "carbure/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"

type MenuItem = {
  title: string
  condition?: boolean
  children: MenuSection[]
}

type MenuSection = Omit<MenuItem, "children"> & {
  icon: string
  path: string
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
        icon: "",
      },
      {
        path: routes.BIOFUELS().RECEIVED,
        title: t("Reçus"),
        icon: "",
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
