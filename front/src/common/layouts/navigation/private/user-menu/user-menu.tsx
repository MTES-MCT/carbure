import { useUser } from "carbure/hooks/user"
import { SimpleMenu } from "common/components/menu2"
import { Text } from "common/components/text"
import css from "./user-menu.module.css"
import { NavLink } from "react-router-dom"
import { ListItem } from "common/components/list2/list-item"
import { useRoutes } from "common/hooks/routes"
import { compact } from "common/utils/collection"
import useEntity from "carbure/hooks/entity"
import { useMemo } from "react"
import {
  AccountLine,
  BarChartLine,
  BookLine,
  ChartLine,
  LogoutBoxLine,
} from "common/components/icon"
import { useTranslation } from "react-i18next"

export const UserMenu = () => {
  const { user, getName } = useUser()
  const { t } = useTranslation()
  const {
    isIndustry,
    isPowerOrHeatProducer,
    isOperator,
    isProducer,
    isAirline,
  } = useEntity()
  const routes = useRoutes()
  const items = useMemo(() => {
    const compactedItems = compact([
      {
        label: t("Mon compte"),
        path: routes.MY_ACCOUNT.INDEX,
        icon: AccountLine,
      },
      (isOperator || isProducer) && {
        label: t("Mes statistiques"),
        path: routes.STATISTICS,
        icon: ChartLine,
      },
      {
        label: t("Statistiques publiques"),
        path: routes.PUBLIC_STATS,
        icon: BarChartLine,
      },
      (isIndustry || isPowerOrHeatProducer || isAirline) && {
        label: t("Annuaire"),
        path: routes.REGISTRY,
        icon: BookLine,
      },
      {
        label: t("Déconnexion"),
        path: routes.LOGOUT,
        icon: LogoutBoxLine,
      },
    ])

    // The last item before logout is the one with the border
    return compactedItems.map((item, index) => ({
      ...item,
      borderBottom: index === compactedItems.length - 2,
    }))
  }, [
    isIndustry,
    isOperator,
    isPowerOrHeatProducer,
    isProducer,
    routes,
    isAirline,
    t,
  ])

  return (
    <SimpleMenu
      buttonProps={{
        iconId: "fr-icon-arrow-down-s-line",
        iconPosition: "right",
        priority: "tertiary",
        size: "small",
        children: <span style={{ maxWidth: "200px" }}>{getName()}</span>,
      }}
      dropdownWidth="300px"
    >
      {({ close }) => (
        <>
          <div className={css["user-menu-infos"]}>
            <Text size="sm" fontWeight="bold">
              {getName()}
            </Text>
            <Text size="sm" fontWeight="regular">
              {user?.email}
            </Text>
          </div>
          {items.map(({ icon: Icon, ...item }) => {
            return (
              <NavLink to={item.path} onClick={close} key={item.path}>
                <ListItem
                  label={item.label}
                  value={item.label}
                  hoverable
                  borderBottom={item.borderBottom}
                  className={css["user-menu-item"]}
                >
                  <Icon size="sm" />
                  {item.label}
                </ListItem>
              </NavLink>
            )
          })}
        </>
      )}
    </SimpleMenu>
  )
}
