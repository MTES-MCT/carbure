import React from "react"
import cl from "clsx"
import styles from "./button.module.css"
import { Loader } from "./icons"
import { SystemProps, AsProp } from "./index"

// BUTTON COMPONENT
type ButtonProps = SystemProps &
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
    [styles.buttonPrimary]: level === "primary",
    [styles.buttonWarning]: level === "warning",
    [styles.buttonDanger]: level === "danger",
    [styles.buttonSuccess]: level === "success",
    [styles.buttonSecondary]: level === "secondary",
  })

  return (
    <Tag
      {...props}
      type={submit ? "submit" : undefined}
      form={typeof submit === "string" ? submit : undefined}
      className={btnClassName}
    >
      {Icon && <Icon />}
      {children}
    </Tag>
  )
}
// ASYNC BUTTON COMPONENT
type AsyncButtonProps = ButtonProps & {
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
// STATUS BUTTON COMPONENT
type StatusButtonProps = ButtonProps & {
  active: boolean
  loading: boolean
  amount: number
  label: string
}

export const StatusButton = ({
  active,
  loading,
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
    <span className={styles.statusButtonAmount}>
      {loading ? <Loader /> : amount}
    </span>
    <span className={styles.statusButtonLabel}>{label}</span>
  </Button>
)
