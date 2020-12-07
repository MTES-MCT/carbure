import React, { useRef } from "react"
import cl from "clsx"

import styles from "./menu.module.css"

import { Dropdown, DropdownItem, DropdownLabel, useDropdown } from "./dropdown"
import { LinkProps } from "react-router-dom"
import { SystemProps } from "."
import { Link } from "../components/relative-route"

type MenuItemProps = SystemProps & React.HTMLProps<HTMLLIElement>

const MenuItem = ({ children, ...props }: MenuItemProps) => (
  <DropdownItem {...props} className={styles.menuItem}>
    {children}
  </DropdownItem>
)

type MenuItemLinkProps = MenuItemProps & LinkProps & { relative?: boolean }

const MenuItemLink = ({ children, ...props }: MenuItemLinkProps) => (
  <DropdownItem className={styles.menuItemLink}>
    <Link {...props}>{children}</Link>
  </DropdownItem>
)

type MenuGroupProps = React.HTMLProps<HTMLUListElement> & {
  label: string
  children: React.ReactNode
}

const MenuGroup = ({ label, children }: MenuGroupProps) => (
  <ul className={styles.menuGroup}>
    <DropdownItem
      className={styles.menuGroupLabel}
      onClick={(e) => e.stopPropagation()}
    >
      {label}
    </DropdownItem>
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
Menu.ItemLink = MenuItemLink

export default Menu
