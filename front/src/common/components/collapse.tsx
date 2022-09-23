import cl from "clsx"
import React, { useState } from "react"
import css from "./collapse.module.css"
import { ChevronDown } from "common/components/icons"

export type CollapseVariant = "info" | "success" | "warning" | "danger"

export interface CollapseProps {
  variant?: CollapseVariant
  icon?: React.FunctionComponent | React.ReactNode
  label?: string
  children?: React.ReactNode
  isOpen?: boolean
}

export const Collapse = ({
  variant,
  icon: Icon,
  label,
  children,
  isOpen = false,
}: CollapseProps) => {
  const [open, setOpen] = useState(isOpen)
  const icon = typeof Icon === "function" ? <Icon /> : Icon

  return (
    <div className={cl(css.collapse, variant && css[variant])}>
      <header onClick={() => setOpen(!open)}>
        {icon}
        {label}
        <ChevronDown className={css.indicator} />
      </header>

      {open && children}
    </div>
  )
}

export default Collapse
