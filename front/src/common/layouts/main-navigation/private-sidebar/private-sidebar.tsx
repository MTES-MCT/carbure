import { Text } from "common/components/text"
import { usePrivateSidebar } from "./private-sidebar.hooks"
import styles from "./private-sidebar.module.css"
import { ChildItem } from "./child-item"

export const PrivateSidebar = () => {
  const menuItems = usePrivateSidebar()
  return (
    <div className={styles["private-sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        <div
          style={{ border: "1px solid red", padding: "20px 0", width: "100%" }}
        ></div>
        <nav>
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
                  <ChildItem child={child} />
                ))}
              </div>
            </div>
          ))}
        </nav>
      </div>

      <div className={styles["bottom-nav"]}>BOTTOM NAV</div>
    </div>
  )
}
