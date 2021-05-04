import React, { useRef } from "react"
import cl from "clsx"
import styles from "./input.module.css"
import { AlertTriangle, Check, IconProps, Search } from "./icons"
import { Box, SystemProps } from "./index"
import { FormChangeHandler } from "common/hooks/use-form"

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

// CHECKBOX COMPONENT

type CheckboxProps = Omit<React.HTMLProps<HTMLDivElement>, "onChange"> & {
  checked?: boolean
  disabled?: boolean
  readOnly?: boolean
  onChange?: FormChangeHandler<any>
}

export const Checkbox = ({
  checked,
  disabled,
  readOnly,
  className,
  onChange,
  ...props
}: CheckboxProps) => {
  const handleChange = onChange
    ? () => onChange({ target: { type: "checkbox", checked: !checked } })
    : undefined

  return (
    <Box
      {...props}
      className={cl(
        styles.checkbox,
        disabled && styles.checkboxDisabled,
        readOnly && styles.checkboxReadOnly,
        className
      )}
      aria-checked={checked}
      aria-disabled={disabled}
      onClick={handleChange}
    >
      {checked ? <Check /> : null}
    </Box>
  )
}

type LabelCheckboxProps = Omit<LabelProps, "onChange"> &
  CheckboxProps & {
    value?: boolean
  }

export const LabelCheckbox = ({
  label,
  className,
  disabled,
  readOnly,
  value,
  checked,
  onChange,
  ...props
}: LabelCheckboxProps) => {
  const id = useRef(Math.random().toString(36).slice(2))

  const handleChange = onChange
    ? () => onChange({ target: { type: "checkbox", checked: !checked } })
    : undefined

  return (
    <label
      id={id.current}
      className={cl(
        styles.labelCheckbox,
        (readOnly || disabled) && styles.disabledLabel,
        className
      )}
      onClick={handleChange}
    >
      <Checkbox
        {...props}
        disabled={disabled}
        checked={checked ?? value}
        onChange={onChange}
        role="checkbox"
        aria-labelledby={id.current}
      />
      {label}
    </label>
  )
}

// SEARCH INPUT COMPONENT

export const SearchInput = ({ className, ...props }: InputProps) => (
  <div className={cl(styles.searchInputWrapper, className)}>
    <Search size={20} color="var(--gray-medium)" />
    <Input {...props} className={styles.searchInput} />
  </div>
)

export const Placeholder = (props: SystemProps) => (
  <div {...props} className={cl(styles.inputPlaceholder, props.className)} />
)
