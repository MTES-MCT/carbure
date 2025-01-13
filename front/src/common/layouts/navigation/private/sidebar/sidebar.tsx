import { Text } from "common/components/text"
import { usePrivateSidebar } from "./sidebar.hooks"
import styles from "./sidebar.module.css"
import { ChildItem } from "./child-item"
import { useTranslation } from "react-i18next"
import { useRoutes } from "common/hooks/routes"
import {
  QuestionLine,
  SettingsFill,
  SettingsLine,
} from "common/components/icon"
import { EntitySelector } from "./entity-selector"
import { useUser } from "carbure/hooks/user"

export const PrivateSidebar = () => {
  const menuItems = usePrivateSidebar()
  const { t } = useTranslation()
  const routes = useRoutes()
  const user = useUser()
  const firstEntity = user.getFirstEntity()

  return (
    <div className={styles["sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        {firstEntity && (
          <EntitySelector className={styles["entity-selector"]} />
        )}
        <nav className={styles["nav"]}>
          {menuItems.map((item) => (
            <div key={item.title}>
              <Text
                size="sm"
                fontWeight="bold"
                className={styles["nav-item-title"]}
              >
                {item.title}
              </Text>
              <div className={styles["nav-item-children"]}>
                {item.children.map((child) => (
                  <ChildItem child={child} key={child.title} />
                ))}
              </div>
            </div>
          ))}
        </nav>
      </div>

      <div className={styles["bottom-nav"]}>
        <ChildItem
          child={{
            path: routes.USER_GUIDE,
            title: t("Guide d'utilisation"),
            target: "_blank",
            icon: QuestionLine,
          }}
        />
        {/* Display settings only if an entity is selected */}
        {firstEntity && (
          <ChildItem
            child={{
              path: routes.SETTINGS,
              title: t("Paramètres de la société"),
              icon: SettingsLine,
              iconActive: SettingsFill,
            }}
          />
        )}
      </div>
    </div>
  )
}
