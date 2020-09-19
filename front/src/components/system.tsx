import React, { CSSProperties } from "react"
import cl from "clsx"

import styles from "./system.module.css"
import { ChevronDown } from "./icons"

type SelectProps = {
  className?: string
  style?: CSSProperties
  children: React.ReactNode
  [k: string]: any // ...props
}

export const Select = ({
  style,
  className,
  children,
  ...props
}: SelectProps) => (
  <div style={style} className={cl(styles.selectWrapper, className)}>
    <select {...props} className={styles.select}>
      {children}
    </select>
    <ChevronDown className={styles.selectArrow} />
  </div>
)

type MenuProps = {
  label: string
  className?: string
  children: React.ReactNode
  [k: string]: any
}

export const Menu = ({ label, className, children, ...props }: MenuProps) => (
  <Select {...props} value="label" className={cl(styles.menu, className)}>
    <option hidden value="label">
      {label}
    </option>
    {children}
  </Select>
)

type ButtonProps = {
  type?: string
  children: React.ReactNode
}

export const Button = ({ type, children, ...props }: ButtonProps) => {
  const className = cl(styles.button, {
    [styles.buttonPrimary]: type === "primary",
  })

  return (
    <button {...props} className={className}>
      {children}
    </button>
  )
}

type AlertProps = {
  type: string
  children: React.ReactNode
  onClose: (event: React.MouseEvent) => void
  [k: string]: any
}

export const Alert = ({ type, children, onClose, ...props }: AlertProps) => {
  const className = cl(styles.alert, {
    [styles.alertWarning]: type === "warning",
    [styles.alertError]: type === "error",
  })

  return (
    <div {...props} className={className}>
      {children}
      <span className={styles.alertHide} onClick={onClose}>
        Masquer ce message
      </span>
    </div>
  )
}
