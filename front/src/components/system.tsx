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
