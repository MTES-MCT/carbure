import React from "react"
import cl from "clsx"
import { NavLink, NavLinkProps } from "react-router-dom"
import styles from "./button.module.css"
import { Loader } from "common-v2/components/icons"
import { SystemProps, AsProp } from "./index"

// BUTTON COMPONENT
export type ButtonProps = SystemProps &
  AsProp &
  React.HTMLProps<HTMLButtonElement> & {
    submit?: string | boolean
    level?: "primary" | "warning" | "danger" | "success" | "secondary"
    icon?: React.ComponentType
  }

export const Button = ({
  as: Tag = "button",
  submit,
  icon: Icon,
  level,
  className,
  children,
  ...props
}: ButtonProps) => {
  const btnClassName = cl(styles.button, className, {
    [styles.buttonIcon]: Boolean(Icon) && !children,
    [styles.buttonPrimary]: level === "primary",
    [styles.buttonWarning]: level === "warning",
    [styles.buttonDanger]: level === "danger",
    [styles.buttonSuccess]: level === "success",
    [styles.buttonSecondary]: level === "secondary",
    [styles.buttonDisabled]: props.disabled,
  })

  return (
    <Tag
      {...props}
      type={submit ? "submit" : undefined}
      form={typeof submit === "string" ? submit : undefined}
      className={btnClassName}
    >
      {Icon && <Icon />}
      {children && <span>{children}</span>}
    </Tag>
  )
}
// ASYNC BUTTON COMPONENT
export type AsyncButtonProps = ButtonProps & {
  loading: boolean
}

export const AsyncButton = ({
  loading,
  icon,
  disabled,
  ...props
}: AsyncButtonProps) => (
  <Button
    {...props}
    icon={loading ? Loader : icon}
    disabled={loading || disabled}
  />
)

export const TabButton = ({ children, className, ...props }: NavLinkProps) => (
  <NavLink
    {...props}
    className={({ isActive }) =>
      cl(
        styles.button,
        styles.statusButton,
        isActive && styles.activeStatusButton,
        className
      )
    }
  >
    <span className={styles.statusButtonLabel}>{children}</span>
  </NavLink>
)
