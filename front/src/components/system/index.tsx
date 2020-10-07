import React, { CSSProperties } from "react"
import cl from "clsx"

import styles from "./index.module.css"

import { Loader, Search } from "./icons"

export type SystemProps = {
  className?: string
  style?: CSSProperties
  children?: React.ReactNode
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
  React.HTMLProps<HTMLButtonElement> & {
    submit?: boolean
    kind?: string
    icon?: React.ComponentType
  }

export const Button = ({
  submit = false,
  icon: Icon,
  kind,
  className,
  children,
  ...props
}: ButtonProps) => {
  const btnClassName = cl(styles.button, className, {
    [styles.buttonPrimary]: kind === "primary",
    [styles.buttonWarning]: kind === "warning",
  })

  return (
    <button
      {...props}
      type={submit ? "submit" : undefined}
      className={btnClassName}
    >
      {Icon && <Icon />}
      {children}
    </button>
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
  amount: number | string
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
    kind?: string
    onClose?: (event: React.MouseEvent) => void
  }

export const Alert = ({
  kind: type,
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

      {onClose && (
        <span className={styles.alertHide} onClick={onClose}>
          Masquer ce message
        </span>
      )}
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

// INPUT COMPONENT

type InputProps = SystemProps & React.HTMLProps<HTMLInputElement>

export const Input = ({ className, ...props }: InputProps) => (
  <input {...props} className={cl(styles.input, className)} />
)

// FORM INPUT COMPONENT

export type LabelInputProps = SystemProps &
  React.HTMLProps<HTMLInputElement> & {
    label: React.ReactNode
  }

export const LabelInput = ({
  label,
  disabled,
  className,
  ...props
}: LabelInputProps) => (
  <label
    className={cl(
      styles.labelWrapper,
      disabled && styles.disabledLabel,
      className
    )}
  >
    {label}
    <Input {...props} disabled={disabled} />
  </label>
)

// TEXT AREA COMPONENT

type LabelTextAreaProps = SystemProps &
  React.HTMLProps<HTMLTextAreaElement> & {
    label: React.ReactNode
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
  ...props
}: LabelInputProps) => (
  <label className={cl(styles.labelCheckbox, className)}>
    <input type="checkbox" {...props} />
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

// TABLE COMPONENT

type TableProps<T> = SystemProps &
  Omit<React.HTMLProps<HTMLTableElement>, "rows"> & {
    rows: T[]
    columns: string[]
    children: (row: T, i: number) => React.ReactNode
    onSelectAll: (e: React.ChangeEvent<HTMLInputElement>) => void
  }

export function Table<T>({
  columns,
  rows,
  children,
  onSelectAll,
  ...props
}: TableProps<T>) {
  return (
    <table {...props} className={styles.table}>
      <thead>
        <tr className={styles.header}>
          <th>
            <input type="checkbox" onChange={onSelectAll} />
          </th>
          {columns.map((column) => (
            <th key={column}>{column}</th>
          ))}
          <th />
        </tr>
      </thead>
      <tbody>{rows.map((row, i) => children(row, i))}</tbody>
    </table>
  )
}

// LOADER OVERLAY

export const LoaderOverlay = () => (
  <Box className={styles.loaderOverlay}>
    <Loader color="var(--black)" size={48} />
  </Box>
)
