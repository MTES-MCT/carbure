import cl from "clsx"
import React, { useState } from "react"
import { Loader } from "common-v2/components/icons"
import css from "./alert.module.css"

export type AlertVariant = "info" | "success" | "warning" | "danger"

export interface AlertProps {
  variant?: AlertVariant
  loading?: boolean
  icon?: React.FunctionComponent | React.ReactNode
  label?: string
  children?: React.ReactNode | CustomRenderer
  style?: React.CSSProperties
  className?: string
}

export const Alert = ({
  variant,
  loading,
  icon: Icon,
  label,
  children,
  className,
  style,
}: AlertProps) => {
  const [open, setOpen] = useState(true)

  if (!open) return null

  const config = {
    close: () => setOpen(false),
  }

  const icon = typeof Icon === "function" ? <Icon /> : Icon
  const child = typeof children === "function" ? children(config) : children

  return (
    <div
      style={style}
      title={label}
      className={cl(
        css.alert,
        className,
        loading && css.loading,
        variant && css[variant]
      )}
    >
      {loading ? <Loader /> : icon}
      {label ?? child}
    </div>
  )
}

type CustomRenderer = (config: { close: () => void }) => React.ReactNode

export default Alert
