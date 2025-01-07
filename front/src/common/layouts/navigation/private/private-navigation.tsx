import { PropsWithChildren, useContext } from "react"
import cl from "clsx"
import { PrivateNavigationContext } from "./private-navigation.context"
import styles from "./private-navigation.module.css"
import { Text } from "common/components/text"
import { PrivateSidebar } from "./sidebar"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { LanguageSelector } from "common/molecules/language-selector"
import { Notifications } from "./notifications"
import { UserMenu } from "./user-menu"
import { NavLink } from "react-router-dom"
import marianne from "common/assets/images/Marianne.svg"
import { ROUTE_URLS } from "common/utils/routes"
import { useRoutes } from "common/hooks/routes"

export const PrivateNavigation = ({ children }: PropsWithChildren) => {
  const { title } = useContext(PrivateNavigationContext)
  const { t } = useTranslation()
  const routes = useRoutes()

  return (
    <>
      <header className={styles.header}>
        <div className={styles["header-left"]}>
          <NavLink to={ROUTE_URLS.HOME} className={styles.logo}>
            <img
              src={marianne}
              alt="marianne logo"
              className={styles.marianne}
            />
            <Text is="h2" size="xl" fontWeight="bold">
              Carbure
            </Text>
          </NavLink>
        </div>
        <div className={styles["header-right"]}>
          <Text is="h1" fontWeight="bold">
            {title}
          </Text>
          <div className={styles["header-right-actions"]}>
            <Button
              priority="tertiary"
              iconPosition="left"
              iconId="ri-question-line"
              size="small"
              linkProps={{ to: routes.CONTACT }}
            >
              {t("Aide")}
            </Button>
            <LanguageSelector />
            <Notifications />
            <UserMenu />
          </div>
        </div>
      </header>
      <div className={cl(styles["body"])}>
        <div className={styles["sidebar"]}>
          <PrivateSidebar />
        </div>

        <section className={styles["page"]}>{children}</section>
      </div>
    </>
  )
}
