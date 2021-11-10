import { useRef } from "react"
import { Link } from "react-router-dom"
import Dropdown, { Anchor } from "./dropdown"
import { ChevronDown } from "./icons"
import Button, { ButtonProps } from "./button"
import List from "./list"
import { Normalizer } from "../hooks/normalize"
import css from "./menu.module.css"
import cl from "clsx"

export interface MenuProps extends ButtonProps {
  className?: string
  style?: React.CSSProperties
  items: MenuItem[]
  label?: string
  anchor?: Anchor
  onAction?: (item: MenuItem) => void
}

export function Menu({
  className,
  items,
  label = "Menu",
  anchor,
  onAction,
  ...props
}: MenuProps) {
  const triggerRef = useRef<HTMLButtonElement>(null)

  return (
    <>
      <Button
        {...props}
        domRef={triggerRef}
        className={cl(css.menu, className)}
      >
        <span>{label}</span>
        <ChevronDown size={20} color="var(--gray-dark)" />
      </Button>

      <Dropdown
        className={css.dropdown}
        triggerRef={triggerRef}
        anchor={anchor}
      >
        {({ close }) => (
          <List
            controlRef={triggerRef}
            className={css.items}
            items={items}
            normalize={normalizeMenu}
            onSelectItem={(item) => {
              item && onAction?.(item)
              close()
            }}
          >
            {(item) => {
              if (item.group) {
                return <b>{item.label}</b>
              } else if (item.value.path) {
                return <Link to={item.value.path}>{item.label}</Link>
              } else {
                return <p>{item.label}</p>
              }
            }}
          </List>
        )}
      </Dropdown>
    </>
  )
}

export interface MenuItem {
  path?: string
  label?: string
  dialog?: ButtonProps["dialog"]
  children?: MenuItem[]
}

export const normalizeMenu: Normalizer<MenuItem> = (item) => ({
  key: item.path ?? item.label ?? "",
  label: item.label ?? item.path ?? "",
  children: item.children,
  disabled: Boolean(item.children),
})

export default Menu
