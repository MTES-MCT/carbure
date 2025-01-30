import { useRef } from "react"
import cl from "clsx"
import { Button, ButtonProps } from "../../button2"
import { Dropdown, DropdownProps } from "../../dropdown2"
import css from "./simple-menu.module.css"

export type SimpleMenuProps = Omit<DropdownProps, "triggerRef"> & {
  label?: string
  buttonProps: ButtonProps
  // If provided, the dropdown will have this width (used for specific cases)
  dropdownWidth?: string
  children: DropdownProps["children"]
}

/**
 * This menu is a simple button with a dropdown.
 * It is used when we want a custom dropdown content.
 */
export const SimpleMenu = ({
  className,
  anchor,
  children,
  dropdownWidth,
  buttonProps,
  ...props
}: SimpleMenuProps) => {
  const ref = useRef<HTMLButtonElement>(null)

  return (
    <>
      <Button {...buttonProps} ref={ref} className={cl(css.menu, className)} />

      <Dropdown
        className={css.dropdown}
        triggerRef={ref}
        anchor={anchor}
        style={{ width: dropdownWidth }}
        {...props}
      >
        {children}
      </Dropdown>
    </>
  )
}
