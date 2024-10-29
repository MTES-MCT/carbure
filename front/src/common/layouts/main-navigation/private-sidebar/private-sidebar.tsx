import { Text } from "common/components/text"
import { usePrivateSidebar } from "./private-sidebar.hooks"
import styles from "./private-sidebar.module.css"
import { NavLink } from "react-router-dom"

export const PrivateSidebar = () => {
  const menuItems = usePrivateSidebar()
  return (
    <div className={styles["private-sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        <div
          style={{ border: "1px solid red", padding: "20px 0", width: "100%" }}
        ></div>
        <nav>
          {menuItems.map((item, index) => (
            <div key={item.title}>
              <Text
                size="sm"
                fontWeight="bold"
                className={styles["nav-item-title"]}
              >
                {item.title}
              </Text>
              <div>
                {item.children.map((child) => (
                  <NavLink
                    key={child.title}
                    to={child.path}
                    className={styles["nav-item-child"]}
                  >
                    {/* <Text is={NavLink} fontWeight="semibold">
                      {child.title}
                    </Text> */}
                  </NavLink>
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
