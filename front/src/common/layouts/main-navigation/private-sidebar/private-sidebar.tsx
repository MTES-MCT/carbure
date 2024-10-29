import { Text } from "common/components/text"
import { usePrivateSidebar } from "./private-sidebar.hooks"
import styles from "./private-sidebar.module.css"
import { NavLink } from "react-router-dom"
import cl from "clsx"

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
              <div>
                {item.children.map(({ icon: Icon, ...child }) => (
                  <NavLink
                    to={child.path}
                    key={child.title}
                    className={({ isActive }) =>
                      cl(
                        styles["nav-item-child"],
                        isActive && styles["nav-item-child--active"]
                      )
                    }
                  >
                    <div className={styles["nav-item-child-content"]}>
                      {Icon && (
                        <Icon className={styles["nav-item-child-icon"]} />
                      )}
                      <Text fontWeight="semibold">{child.title}</Text>
                    </div>
                    {child.additionalInfo && (
                      <Text
                        fontWeight="semibold"
                        className={styles["nav-item-child-additional-info"]}
                      >
                        {child.additionalInfo}
                      </Text>
                    )}
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
