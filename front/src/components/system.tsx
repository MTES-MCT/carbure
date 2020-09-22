import React, { CSSProperties } from "react"
import { useHistory } from "react-router-dom"
import cl from "clsx"

import styles from "./system.module.css"
import { ChevronDown } from "./icons"

type SystemProps = {
  className?: string
  style?: CSSProperties
  children: React.ReactNode
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
