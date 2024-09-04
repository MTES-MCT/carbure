import { useRef } from "react"
import { Link } from "react-router-dom"
import cl from "clsx"
import Dropdown from "./dropdown"
import { ChevronDown } from "./icons"
import Button, { ButtonProps } from "./button"
import List from "./list"
import { Normalizer } from "../utils/normalize"
import css from "./menu.module.css"

export interface MenuProps extends ButtonProps {
  className?: string
  style?: React.CSSProperties
  items: MenuItem[]
  label?: string
  anchor?: string
  onAction?: (key: string) => void
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
        <span style={{ maxWidth: "200px" }}>{label}</span>
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
            onSelectValue={(item) => {
              item !== undefined && onAction?.(item)
              close()
            }}
          >
            {(item) => {
              if (item.group) {
                return <b>{item.label}</b>
              } else if (item.data.path) {
                return (
                  <Link to={item.data.path} onClick={(e) => e.preventDefault()}>
                    {item.label}
                  </Link>
                )
              } else {
                return <p onClick={item.data.action}>{item.label}</p>
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
  action?: () => void
  children?: MenuItem[]
}

export const normalizeMenu: Normalizer<MenuItem, string> = (item) => ({
  value: item.path ?? item.label ?? "",
  label: item.label ?? item.path ?? "",
  children: item.children,
  disabled: Boolean(item.children),
})

export default Menu
