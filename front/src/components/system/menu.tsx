import React, { useRef } from "react"
import cl from "clsx"

import styles from "./menu.module.css"

import { Dropdown, DropdownLabel, useDropdown } from "./dropdown"
import { Link } from "react-router-dom"
import { SystemProps } from "."

type MenuItemProps = React.HTMLProps<HTMLLIElement> & {
  to?: string
  children: React.ReactNode
}

const MenuItem = ({ to, children, ...props }: MenuItemProps) => (
  <li {...props} className={to ? styles.menuItemLink : styles.menuItem}>
    {to ? <Link to={to}>{children}</Link> : children}
  </li>
)

type MenuGroupProps = React.HTMLProps<HTMLUListElement> & {
  label: string
  children: React.ReactNode
}

const MenuGroup = ({ label, children }: MenuGroupProps) => (
  <ul className={styles.menuGroup}>
    <li className={styles.menuGroupLabel} onClick={(e) => e.stopPropagation()}>
      {label}
    </li>
    {children}
  </ul>
)

export type MenuProps = SystemProps & React.HTMLProps<HTMLDivElement>

const Menu = ({ children, label, className, ...props }: MenuProps) => {
  const container = useRef<HTMLDivElement>(null)
  const dd = useDropdown()

  return (
    <div
      {...props}
      ref={container}
      className={cl(styles.menu, className)}
      onClick={dd.toggle}
    >
      <DropdownLabel
        className={styles.menuLabel}
        onEnter={() => dd.toggle(true)}
      >
        {label}
      </DropdownLabel>

      {dd.isOpen && container.current && (
        <Dropdown end parent={container.current} className={styles.menuItems}>
          {children}
        </Dropdown>
      )}
    </div>
  )
}

Menu.Group = MenuGroup
Menu.Item = MenuItem

export default Menu
