import { NavLink, useMatch } from "react-router-dom"
import { MenuItem } from "../private-sidebar.types"
import styles from "./child-item.module.css"
import cl from "clsx"
import { Text } from "common/components/text"

type ChildItemProps = {
  child: MenuItem
}

export const ChildItem = ({ child }: ChildItemProps) => {
  const Icon = child.icon
  const IconActive = child.iconActive

  const isActive = useMatch(child.path)

  return (
    <NavLink
      to={child.path}
      key={child.title}
      className={cl(
        styles["nav-item-child"],
        isActive && styles["nav-item-child--active"]
      )}
      target={child.target}
    >
      <div className={styles["nav-item-child-content"]}>
        {/* Display the icon only if it's not the current page */}
        {/* Or, display the icon only if the iconActive is not defined */}
        {((Icon && !isActive) || (!IconActive && Icon)) && (
          <Icon className={styles["nav-item-child-icon"]} />
        )}
        {IconActive && isActive && (
          <IconActive className={styles["nav-item-child-icon"]} />
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
  )
}
