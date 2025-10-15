import { Text } from "common/components/text"
import { usePrivateSidebar } from "./sidebar.hooks"
import styles from "./sidebar.module.css"
import { ChildItem } from "./child-item"
import { useTranslation } from "react-i18next"
import { useRoutes } from "common/hooks/routes"
import { EntitySelector } from "./entity-selector"
import { useUser } from "common/hooks/user"
import useEntity from "common/hooks/entity"

export const PrivateSidebar = () => {
  const menuItems = usePrivateSidebar()
  const { t } = useTranslation()
  const routes = useRoutes()
  const user = useUser()
  const firstEntity = user.getFirstEntity()
  const entity = useEntity()

  return (
    <div className={styles["sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        {firstEntity && (
          <EntitySelector className={styles["entity-selector"]} />
        )}
        <nav className={styles["nav"]}>
          {menuItems.map(({ badge: Badge, ...item }) => (
            <div key={item.title}>
              <Text
                size="sm"
                fontWeight="bold"
                className={styles["nav-item-title"]}
                // DSFR Badge is a p, and we can't use a <p> inside a <p>
                is={Badge ? "span" : "p"}
              >
                {item.title}
                {Badge ?? null}
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
            icon: "ri-question-line",
          }}
        />
        {/* Display settings only if an entity is selected */}
        {entity.id !== -1 && (
          <ChildItem
            child={{
              path: routes.SETTINGS.ROOT,
              title: t("Paramètres de la société"),
              icon: "ri-settings-3-line",
              iconActive: "ri-settings-3-fill",
            }}
          />
        )}
      </div>
    </div>
  )
}
