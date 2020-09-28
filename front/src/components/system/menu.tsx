import React from "react"
import cl from "clsx"

import styles from "./menu.module.css"

import { Dropdown, useDropdown, DropdownProps } from "./dropdown"

type MenuItemProps = React.HTMLProps<HTMLLIElement> & {
  children: React.ReactNode
}

const MenuItem = ({ children, ...props }: MenuItemProps) => (
  <li {...props} className={styles.menuItem}>
    {children}
  </li>
)

type MenuGroupProps = React.HTMLProps<HTMLUListElement> & {
  label: string
  children: React.ReactNode
}

const MenuGroup = ({ label, children }: MenuGroupProps) => (
  <ul className={styles.menuGroup}>
    <li className={styles.menuGroupLabel}>{label}</li>
    {children}
  </ul>
)

const Menu = ({ children, label, className, ...props }: DropdownProps) => {
  const dd = useDropdown()

  return (
    <Dropdown
      {...props}
      className={cl(styles.menu, className)}
      onClick={dd.toggle}
    >
      <Dropdown.Label className={styles.menuLabel}>{label}</Dropdown.Label>
      <Dropdown.Items open={dd.isOpen}>{children}</Dropdown.Items>
    </Dropdown>
  )
}

Menu.Group = MenuGroup
Menu.Item = MenuItem

export default Menu
