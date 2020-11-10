import React, { CSSProperties } from "react"
import cl from "clsx"

import styles from "./index.module.css"

import { AlertTriangle, Loader, Search } from "./icons"

export type SystemProps = {
  className?: string
  style?: CSSProperties
  children?: React.ReactNode
}

type AsProp = {
  as?: string | React.ComponentType<any>
}

type BoxProps = SystemProps &
  React.HTMLProps<HTMLDivElement> & {
    row?: boolean
    as?: string | React.ComponentType<any>
  }

export const Box = ({
  row = false,
  as: Component = "div",
  className,
  children,
  ...props
}: BoxProps) => (
  <Component
    {...props}
    className={cl(styles.box, row && styles.boxRow, className)}
  >
    {children}
  </Component>
)

export const Main = (props: BoxProps) => <Box {...props} as="main" />

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

// TITLE COMPONENT

type TitleProps = SystemProps & React.HTMLProps<HTMLHeadingElement>

export const Title = ({ children, className, ...props }: TitleProps) => (
  <h1 {...props} className={cl(styles.title, className)}>
    {children}
  </h1>
)

// INPUT COMPONENT

type InputProps = SystemProps &
  React.InputHTMLAttributes<HTMLInputElement> & {
    error?: string
  }

export const Input = ({ className, error, ...props }: InputProps) => (
  <input {...props} className={cl(styles.input, className)} />
)

// FORM INPUT COMPONENT

export type LabelInputProps = InputProps & {
  label: React.ReactNode
  error?: string
}

export const LabelInput = ({
  label,
  disabled,
  error,
  className,
  ...props
}: LabelInputProps) => (
  <label
    title={error}
    className={cl(
      styles.labelWrapper,
      disabled && styles.disabledLabel,
      error && styles.errorLabel,
      className
    )}
  >
    <span>
      {label}
      {error && <AlertTriangle size={16} />}
    </span>
    <Input {...props} disabled={disabled} />
  </label>
)

// TEXT AREA COMPONENT

type LabelTextAreaProps = SystemProps &
  React.HTMLProps<HTMLTextAreaElement> & {
    label: React.ReactNode
    error?: string
  }

export const LabelTextArea = ({
  label,
  className,
  ...props
}: LabelTextAreaProps) => (
  <label className={cl(styles.labelWrapper, styles.labelTextArea)}>
    {label}
    <textarea {...props} className={styles.textarea} />
  </label>
)

// LABEL CHECKBOX COMPONENT
export const LabelCheckbox = ({
  label,
  className,
  disabled,
  ...props
}: LabelInputProps) => (
  <label
    className={cl(
      styles.labelCheckbox,
      disabled && styles.disabledLabel,
      className
    )}
  >
    <input type="checkbox" disabled={disabled} {...props} />
    {label}
  </label>
)

// SEARCH INPUT COMPONENT

export const SearchInput = ({ className, ...props }: InputProps) => (
  <div className={cl(styles.searchInputWrapper, className)}>
    <Search size={20} color="var(--gray-medium)" />
    <Input {...props} className={styles.searchInput} />
  </div>
)

// LOADER OVERLAY

export const LoaderOverlay = () => (
  <Box className={styles.loaderOverlay}>
    <Loader color="var(--black)" size={48} />
  </Box>
)
