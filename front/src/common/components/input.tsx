import React from "react"
import cl from "clsx"
import styles from "./input.module.css"
import { AlertTriangle, Search } from "./icons"
import { SystemProps } from "./index"

// INPUT COMPONENT

export type InputProps = SystemProps &
  React.InputHTMLAttributes<HTMLInputElement> & {
    innerRef?: React.Ref<HTMLInputElement>
  }

export const Input = ({ className, innerRef, ...props }: InputProps) => (
  <input {...props} ref={innerRef} className={cl(styles.input, className)} />
)
// LABEL COMPONENT

export type LabelProps = SystemProps &
  Omit<React.HTMLProps<HTMLLabelElement>, "value" | "onChange"> & {
    error?: string | null
    tooltip?: string
    label: string
  }

export const Label = ({
  className,
  disabled,
  error,
  tooltip,
  label,
  children,
  ...props
}: LabelProps) => (
  <label
    {...props}
    title={error ? error : tooltip}
    className={cl(
      styles.labelWrapper,
      disabled && styles.disabledLabel,
      error && styles.errorLabel,
      className
    )}
  >
    <span className={styles.labelText}>
      {label}
      {error && <AlertTriangle size={16} />}
    </span>
    {children}
  </label>
)
// FORM INPUT COMPONENT

export type LabelInputProps = InputProps & {
  label: string
  error?: string
  tooltip?: string
}

export const LabelInput = ({
  label,
  disabled,
  error,
  tooltip,
  className,
  ...props
}: LabelInputProps) => (
  <Label
    disabled={disabled}
    error={error}
    tooltip={tooltip}
    label={label}
    className={className}
  >
    <Input {...props} disabled={disabled} />
  </Label>
)

// TEXT AREA COMPONENT
type LabelTextAreaProps = SystemProps &
  React.HTMLProps<HTMLTextAreaElement> & {
    label: string
    error?: string
  }

export const LabelTextArea = ({
  label,
  className,
  ...props
}: LabelTextAreaProps) => (
  <Label label={label} className={cl(styles.labelTextArea, className)}>
    <textarea {...props} className={styles.textarea} />
  </Label>
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
