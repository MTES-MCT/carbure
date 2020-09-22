import React, { CSSProperties } from "react"
import { useHistory } from "react-router-dom"
import cl from "clsx"

import styles from "./system.module.css"
import { ChevronDown } from "./icons"

type SystemProps = {
  className?: string
  style?: CSSProperties
  children?: React.ReactNode
}

// SELECT COMPONENT

type SelectProps = SystemProps & React.HTMLProps<HTMLSelectElement>

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

// MENU COMPONENT

export const Menu = ({ className, children, ...props }: SelectProps) => (
  <Select {...props} className={cl(styles.menu, className)}>
    {children}
  </Select>
)

// MENU LINK COMPONENT

type MenuLinkProps = SystemProps &
  React.HTMLProps<HTMLOptionElement> & {
    to: string
  }

export const MenuLink = ({ to, children, ...props }: MenuLinkProps) => {
  const history = useHistory()

  return (
    <option {...props} onClick={() => history.push(to)}>
      {children}
    </option>
  )
}

// BUTTON COMPONENT

type ButtonProps = SystemProps &
  React.HTMLProps<HTMLButtonElement> & {
    type?: string
  }

export const Button = ({
  type,
  className,
  children,
  ...props
}: ButtonProps) => {
  const btnClassName = cl(styles.button, className, {
    [styles.buttonPrimary]: type === "primary",
  })

  return (
    <button {...props} className={btnClassName}>
      {children}
    </button>
  )
}

// STATUS BUTTON COMPONENT

type StatusButtonProps = ButtonProps & {
  active: boolean
  amount: number
  label: string
}

export const StatusButton = ({
  active,
  amount,
  label,
  className,
  ...props
}: StatusButtonProps) => (
  <Button
    {...props}
    className={cl(
      styles.statusButton,
      active && styles.activeStatusButton,
      className
    )}
  >
    <span>{amount}</span>
    <span className={styles.statusButtonLabel}>{label}</span>
  </Button>
)

// ALERT COMPONENT

type AlertProps = SystemProps &
  React.HTMLProps<HTMLDivElement> & {
    type?: string
    onClose: (event: React.MouseEvent) => void
  }

export const Alert = ({
  type,
  children,
  className,
  onClose,
  ...props
}: AlertProps) => {
  const divClassName = cl(styles.alert, className, {
    [styles.alertWarning]: type === "warning",
    [styles.alertError]: type === "error",
  })

  return (
    <div {...props} className={divClassName}>
      {children}
      <span className={styles.alertHide} onClick={onClose}>
        Masquer ce message
      </span>
    </div>
  )
}

// TITLE COMPONENT
type TitleProps = SystemProps & React.HTMLProps<HTMLHeadingElement>

export const Title = ({ children, className, ...props }: TitleProps) => (
  <h1 {...props} className={cl(styles.title, className)}>
    {children}
  </h1>
)
