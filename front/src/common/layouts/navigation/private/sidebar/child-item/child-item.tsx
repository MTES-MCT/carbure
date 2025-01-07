import { NavLink, useLocation } from "react-router-dom"
import { MenuItem } from "../private-sidebar.types"
import styles from "./child-item.module.css"
import cl from "clsx"
import { Text } from "common/components/text"
import { useMemo } from "react"
import { useYearsProvider } from "common/providers/years-provider"

type ChildItemProps = {
  child: MenuItem
}

export const ChildItem = ({ child }: ChildItemProps) => {
  const Icon = child.icon
  const IconActive = child.iconActive
  const location = useLocation()
  const { selectedYear, root } = useYearsProvider()

  // Check if the current url starts with the child path
  const isActive = useMemo(
    () => location.pathname.startsWith(child.path),
    [location.pathname, child.path]
  )

  // Replace the year in the url for all subpages of a section
  const url = useMemo(() => {
    const rx = new RegExp(`${root}/[0-9]+`)
    const replacement = `${root}/${selectedYear}`

    return child.path.includes(root)
      ? child.path.replace(rx, replacement)
      : child.path
  }, [child.path, root, selectedYear])

  return (
    <NavLink
      to={url}
      key={child.title}
      className={({ isActive }) =>
        cl(
          isActive && styles["nav-item-child--active"],
          styles["nav-item-child"]
        )
      }
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
