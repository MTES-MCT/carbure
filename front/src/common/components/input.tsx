import React, { useRef } from "react"
import cl from "clsx"
import styles from "./input.module.css"
import {
  AlertTriangle,
  Check,
  IconProps,
  Upload,
} from "common-v2/components/icons"
import { Box, SystemProps } from "./index"
import { AsyncButton, AsyncButtonProps } from "./button"
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
  Omit<React.HTMLProps<HTMLLabelElement>, "value" | "onChange" | "label"> & {
    error?: string | null
    tooltip?: string
    label?: React.ReactNode
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
    title={[error ?? '', tooltip, typeof label === "string" ? label : ''].find(Boolean)} // prettier-ignore
    className={cl(
      styles.labelWrapper,
      !readOnly && disabled && styles.disabledLabel,
      error && styles.errorLabel,
      (disabled || readOnly) && styles.readonlyLabel,
      className
    )}
  >
    <div className={styles.labelText}>
      {error && <AlertTriangle size={16} />}
      {label}
      {!readOnly && required && " *"}
    </div>
    {children}
    {Icon && <Icon className={styles.labelIcon} />}
  </label>
)

// FORM INPUT COMPONENT

export type LabelInputProps = InputProps & {
  label?: string
  error?: string
  tooltip?: string
  icon?: React.ComponentType<IconProps>
}

export const LabelInput = ({
  label,
  disabled,
  error,
  tooltip,
  className,
  required,
  style,
  icon,
  ...props
}: LabelInputProps) => (
  <Label
    required={required}
    disabled={disabled}
    error={error}
    tooltip={tooltip}
    label={label}
    icon={icon}
    readOnly={props.readOnly}
    className={className}
    style={style}
  >
    <Input {...props} disabled={disabled} />
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
  name,
  onChange,
  ...props
}: CheckboxProps) => {
  const handleChange = onChange
    ? () => onChange({ target: { type: "checkbox", checked: !checked, name } })
    : undefined

  return (
    <Box
      {...props}
      className={cl(
        styles.checkbox,
        checked && styles.checkboxChecked,
        disabled && styles.checkboxDisabled,
        readOnly && styles.checkboxReadOnly,
        className
      )}
      aria-checked={checked}
      aria-disabled={disabled}
      onClick={handleChange}
    >
      {checked ? <Check stroke={3} /> : null}
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
  name,
  onChange,
  ...props
}: LabelCheckboxProps) => {
  const id = useRef(Math.random().toString(36).slice(2))

  const handleChange = onChange
    ? () => onChange({ target: { type: "checkbox", checked: !checked, name } })
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
        name={name}
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

type FileInputProps = Omit<AsyncButtonProps, "value" | "onChange"> & {
  placeholder?: string
  value: File | undefined
  onChange: (value: File | undefined) => void
}

export const FileInput = ({
  placeholder,
  value,
  onChange,
  ...props
}: FileInputProps) => {
  return (
    <AsyncButton
      as="label"
      level={value ? "success" : "primary"}
      icon={value ? Check : Upload}
      {...props}
    >
      <input
        hidden
        type="file"
        onChange={(e) => onChange(e!.target.files![0])}
      />
      {value ? value.name : placeholder}
    </AsyncButton>
  )
}
