import { NavLink } from "react-router-dom"
import { MenuItem } from "../private-sidebar.types"
import styles from "./child-item.module.css"
import cl from "clsx"
import { Text } from "common/components/text"

type ChildItemProps = {
  child: MenuItem
}

export const ChildItem = ({ child }: ChildItemProps) => {
  const Icon = child.icon
  return (
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
        {Icon && <Icon className={styles["nav-item-child-icon"]} />}
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
