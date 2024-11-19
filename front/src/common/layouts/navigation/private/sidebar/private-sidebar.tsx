import { Text } from "common/components/text"
import { usePrivateSidebar } from "./private-sidebar.hooks"
import styles from "./private-sidebar.module.css"
import { ChildItem } from "./child-item"
import { useTranslation } from "react-i18next"
import { useRoutes } from "common/hooks/routes"
import {
  QuestionLine,
  SettingsFill,
  SettingsLine,
} from "common/components/icon"
import { EntitySelector } from "./entity-selector"
import useEntity from "carbure/hooks/entity"
import { useUser } from "carbure/hooks/user"
import { Button } from "common/components/button2"

export const PrivateSidebar = () => {
  const menuItems = usePrivateSidebar()
  const { t } = useTranslation()
  const routes = useRoutes()
  const { isBlank } = useEntity()
  const user = useUser()
  const firstEntity = user.getFirstEntity()

  return (
    <div className={styles["private-sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        {isBlank && !firstEntity && (
          <Button
            priority="tertiary"
            linkProps={{ to: routes.MY_ACCOUNT.ADD_COMPANY }}
            iconId="ri-add-line"
          >
            {t("Lier le compte à des sociétés")}
          </Button>
        )}

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
