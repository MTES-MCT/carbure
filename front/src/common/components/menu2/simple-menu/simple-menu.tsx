import { useRef } from "react"
import cl from "clsx"
import { Button, ButtonProps } from "../../button2"
import { Dropdown, DropdownProps } from "../../dropdown2"
import css from "./simple-menu.module.css"

export type SimpleMenuProps = {
  className?: string
  label?: string
  anchor?: string
  children: DropdownProps["children"]
  buttonProps: ButtonProps
  // If provided, the dropdown will have this width (used for specific cases)
  dropdownWidth?: string
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
}: SimpleMenuProps) => {
  const triggerRef = useRef<HTMLButtonElement>(null)

  return (
    <>
      <Button
        {...buttonProps}
        ref={triggerRef}
        className={cl(css.menu, className)}
      />

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
