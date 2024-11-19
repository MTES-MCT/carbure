import { useRef } from "react"
import cl from "clsx"
import { Button, ButtonProps } from "../../button2"
import { Dropdown, DropdownProps } from "../../dropdown2"
import css from "./simple-menu.module.css"

export type SimpleMenuProps = Omit<ButtonProps, "children" | "title"> & {
  className?: string
  style?: React.CSSProperties
  label?: string
  anchor?: string
  children: DropdownProps["children"]

  // If provided, the dropdown will have this width (used for specific cases)
  dropdownWidth?: string
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
  dropdownWidth,
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
        style={{ width: dropdownWidth }}
      >
        {children}
      </Dropdown>
    </>
  )
}
