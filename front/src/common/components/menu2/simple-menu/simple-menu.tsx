import { useRef } from "react"
import cl from "clsx"
import { Button, ButtonProps } from "../../button2"
import { Dropdown } from "../../dropdown2"
import css from "./simple-menu.module.css"

export type SimpleMenuProps = Exclude<ButtonProps, "children" | "title"> & {
  className?: string
  style?: React.CSSProperties
  label?: string
  anchor?: string
  children: React.ReactNode
}

/**
 * This menu is a simple button with a dropdown.
 * It is used when we want a custom dropdown content.
 */
export const SimpleMenu = ({
  className,
  label = "Menu",
  anchor,
  children,
  ...props
}: SimpleMenuProps) => {
  const triggerRef = useRef<HTMLButtonElement>(null)

  return (
    <>
      <Button {...props} ref={triggerRef} className={cl(css.menu, className)}>
        <span style={{ maxWidth: "200px" }}>{label}</span>
      </Button>

      <Dropdown
        className={css.dropdown}
        triggerRef={triggerRef}
        anchor={anchor}
      >
        {children}
      </Dropdown>
    </>
  )
}
