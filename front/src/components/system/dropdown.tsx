import React, { useEffect, useState } from "react"
import cl from "clsx"

import styles from "./dropdown.module.css"

import { SystemProps } from "."
import { ChevronDown } from "./icons"

export function useDropdown() {
  const [isOpen, setOpen] = useState(false)

  function toggle(value?: any) {
    if (typeof value === "boolean") {
      setOpen(value)
    } else {
      setOpen(!isOpen)
    }
  }

  // close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return

    const close = () => setOpen(false)

    function onEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        close()
      }
    }

    window.addEventListener("click", close)
    window.addEventListener("keydown", onEscape)

    return () => {
      window.removeEventListener("click", close)
      window.removeEventListener("keydown", onEscape)
    }
  }, [isOpen])

  return { isOpen, toggle }
}

type DropdownLabelProps = SystemProps & React.HTMLProps<HTMLDivElement>

const DropdownLabel = ({
  children,
  className,
  ...props
}: DropdownLabelProps) => (
  <div {...props} className={cl(styles.dropdownLabel, className)}>
    {children}
    <ChevronDown className={styles.dropdownArrow} />
  </div>
)

type DropdownItemsProps = SystemProps &
  React.HTMLProps<HTMLUListElement> & {
    open: boolean
    children: React.ReactNode
  }

const DropdownItems = ({
  open,
  children,
  className,
  ...props
}: DropdownItemsProps) => {
  if (!open) return null

  return (
    <ul
      {...props}
      className={cl("dropdown-items", styles.dropdownItems, className)}
    >
      {children}
    </ul>
  )
}

export type DropdownProps = SystemProps & React.HTMLProps<HTMLDivElement>

export const Dropdown = ({ className, children, ...props }: DropdownProps) => (
  <div {...props} className={cl(styles.dropdown, className)}>
    {children}
  </div>
)

Dropdown.Label = DropdownLabel
Dropdown.Items = DropdownItems

export default Dropdown
