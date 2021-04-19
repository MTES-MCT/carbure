import React from "react"
import cl from "clsx"
import styles from "./input.module.css"
import { AlertTriangle, IconProps, Search } from "./icons"
import { SystemProps } from "./index"

// INPUT COMPONENT

export type InputProps = SystemProps &
  React.InputHTMLAttributes<HTMLInputElement> & {
    innerRef?: React.Ref<HTMLInputElement>
  }

export const Input = ({ className, innerRef, ...props }: InputProps) => (
  <input
    {...props}
    disabled={!props.readOnly && props.disabled}
    type={props.readOnly ? "text" : props.type}
    ref={innerRef}
    placeholder={props.readOnly ? "N/A" : props.placeholder}
    className={cl(styles.input, className)}
  />
)
// LABEL COMPONENT

export type LabelProps = SystemProps &
  Omit<React.HTMLProps<HTMLLabelElement>, "value" | "onChange"> & {
    error?: string | null
    tooltip?: string
    label?: string
    required?: boolean
    icon?: React.ComponentType<IconProps>
  }

export const Label = ({
  className,
  disabled,
  error,
  tooltip,
  label,
  readOnly,
  required = false,
  icon: Icon,
  children,
  ...props
}: LabelProps) => (
  <label
    {...props}
    title={error ? error : tooltip}
    className={cl(
      styles.labelWrapper,
      !readOnly && disabled && styles.disabledLabel,
      error && styles.errorLabel,
      className
    )}
  >
    <span className={styles.labelText}>
      {label}
      {!readOnly && required && " *"}
      {error && <AlertTriangle size={16} />}
    </span>
    {children}
    {Icon && <Icon className={styles.labelIcon} />}
  </label>
)
// FORM INPUT COMPONENT

export type LabelInputProps = InputProps & {
  label?: string
  error?: string
  tooltip?: string
}

export const LabelInput = ({
  label,
  disabled,
  error,
  tooltip,
  className,
  required,
  style,
  ...props
}: LabelInputProps) => (
  <Label
    required={required}
    disabled={disabled}
    error={error}
    tooltip={tooltip}
    label={label}
    className={className}
    readOnly={props.readOnly}
    style={style}
  >
    <Input {...props} disabled={disabled} />
  </Label>
)

// TEXT AREA COMPONENT
export type LabelTextAreaProps = SystemProps &
  React.HTMLProps<HTMLTextAreaElement> & {
    label?: string
    error?: string
  }

export const LabelTextArea = ({
  label,
  className,
  ...props
}: LabelTextAreaProps) => (
  <Label
    label={label}
    readOnly={props.readOnly}
    className={cl(styles.labelTextArea, className)}
  >
    <textarea
      {...props}
      className={styles.textarea}
      placeholder={props.readOnly ? "N/A" : props.placeholder}
    />
  </Label>
)

// LABEL CHECKBOX COMPONENT

type LabelCheckboxProps = Omit<LabelInputProps, "value"> & {
  value?: boolean
}

export const LabelCheckbox = ({
  label,
  className,
  disabled,
  readOnly,
  value,
  checked,
  ...props
}: LabelCheckboxProps) => (
  <label
    className={cl(
      styles.labelCheckbox,
      (readOnly || disabled) && styles.disabledLabel,
      className
    )}
  >
    <input
      {...props}
      type="checkbox"
      disabled={disabled}
      checked={checked ?? value}
    />
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

export const Placeholder = () => <div className={styles.inputPlaceholder} />
