import React, { useEffect, useRef, useState } from "react"
import cl from "clsx"
import Button from "./button"
import { AlertTriangle, Cross, Loader, Search } from "./icons"
import css from "./input.module.css"
import { layout, Layout } from "./scaffold"

export type FieldVariant = "outline" | "solid" | "inline" | "text"

export interface Control extends Layout {
  className?: string
  style?: React.CSSProperties
  variant?: FieldVariant
  clear?: boolean
  disabled?: boolean
  readOnly?: boolean
  required?: boolean
  loading?: boolean
  error?: string
  label?: string
  type?: string
  name?: string
  placeholder?: string
  icon?: React.FunctionComponent | React.ReactNode
  domRef?: React.RefObject<HTMLElement>
}

export interface TextInputProps extends Control {
  value: string | undefined
  onChange: (value: string | undefined) => void
}

export const TextInput = ({
  clear,
  value,
  onChange,
  ...props
}: TextInputProps) => (
  <Input
    {...props}
    value={value ?? ""}
    onChange={(e) => onChange(e.target.value)}
    onClear={clear && value ? () => onChange(undefined) : undefined}
  />
)

export interface NumberInputProps extends Control {
  min?: number
  max?: number
  step?: number
  value: number | undefined
  onChange: (value: number | undefined) => void
}

export const NumberInput = ({
  clear,
  value,
  onChange,
  ...props
}: NumberInputProps) => (
  <Input
    {...props}
    type="number"
    value={value ?? ""}
    onClear={clear && value ? () => onChange(undefined) : undefined}
    onChange={(e) => {
      const value = parseFloat(e.target.value)
      const change = isNaN(value) ? undefined : value
      onChange(change)
    }}
  />
)

export interface DateInputProps extends Control {
  value: string | undefined
  onChange: (value: string | undefined) => void
}

export const DateInput = ({
  clear,
  value,
  onChange,
  ...props
}: DateInputProps) => (
  <Input
    {...props}
    type="date"
    value={value ?? ""}
    onChange={(e) => onChange(e.target.value)}
    onClear={clear && value ? () => onChange(undefined) : undefined}
  />
)

export interface FileInputProps extends Control {
  value: File | undefined
  onChange: (value: File | undefined) => void
}

export const FileInput = ({
  clear,
  placeholder = "Select a file",
  value,
  onChange,
  ...props
}: FileInputProps) => (
  <Field
    {...props}
    onClear={clear && value ? () => onChange(undefined) : undefined}
  >
    <label tabIndex={0} className={css.file}>
      <input
        hidden
        disabled={props.disabled}
        readOnly={props.readOnly}
        required={props.required}
        name={props.name}
        type="file"
        onChange={(e) => onChange(e.target.files?.[0])}
      />
      {value?.name ?? placeholder}
    </label>
  </Field>
)

export interface InputProps extends Control {
  min?: number
  max?: number
  step?: number
  value: string | number | undefined
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  onClear?: () => void
}

export const Input = ({
  type,
  name,
  placeholder,
  min,
  max,
  step,
  value,
  onChange,
  onClear,
  ...props
}: InputProps) => (
  <Field {...props} onClear={onClear}>
    <input
      title={`${value}`}
      disabled={props.disabled}
      readOnly={props.readOnly}
      required={props.required}
      type={type}
      name={name}
      placeholder={placeholder}
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={onChange}
    />
  </Field>
)

export interface TextAreaProps extends Control {
  rows?: number
  cols?: number
  value: string | undefined
  onChange: (value: string | undefined) => void
}

export const TextArea = ({
  rows,
  cols,
  clear,
  name,
  placeholder,
  value,
  onChange,
  ...props
}: TextAreaProps) => (
  <Field
    {...props}
    onClear={clear && value ? () => onChange(undefined) : undefined}
  >
    <textarea
      title={value}
      rows={rows}
      cols={cols}
      disabled={props.disabled}
      readOnly={props.readOnly}
      required={props.required}
      name={name}
      placeholder={placeholder}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
    />
  </Field>
)

export interface SearchInputProps extends TextInputProps {
  debounce?: number
}

export const SearchInput = ({
  className,
  clear,
  name,
  placeholder,
  debounce,
  value,
  onChange,
  ...props
}: SearchInputProps) => {
  const timeoutRef = useRef<number>()
  const [search, setSearch] = useState(value ?? "")

  useEffect(() => {
    setSearch(value ?? "")
  }, [value])

  function debouncedSearch(search: string) {
    if (!debounce) return onChange(search)

    setSearch(search)
    timeoutRef.current && window.clearTimeout(timeoutRef.current)
    timeoutRef.current = window.setTimeout(() => onChange(search), debounce)
  }

  return (
    <Field
      {...props}
      className={cl(css.search, className)}
      onClear={clear && search ? () => onChange(undefined) : undefined}
    >
      <div className={css.icon}>
        <Search />
      </div>

      <input
        title={search}
        disabled={props.disabled}
        readOnly={props.readOnly}
        required={props.required}
        name={name}
        placeholder={placeholder ?? "Rechercher..."}
        value={search ?? ""}
        onChange={(e) => debouncedSearch(e.target.value)}
      />
    </Field>
  )
}

export interface GroupFieldProps extends Control {
  children?: React.ReactNode
}

export const GroupField = ({
  domRef,
  aside,
  spread,
  disabled,
  readOnly,
  loading,
  required,
  error,
  label,
  variant,
  className,
  style,
  children,
}: GroupFieldProps) => {
  return (
    <div
      data-field
      data-disabled={disabled ? true : undefined}
      data-readonly={readOnly ? true : undefined}
      data-loading={loading ? true : undefined}
      data-error={error ? true : undefined}
      style={style}
      className={cl(css.field, variant && css[variant], className)}
      {...layout({ aside, spread })}
    >
      {label && (
        <label className={css.label} title={label}>
          {label}
          {required && " *"}
        </label>
      )}

      <div
        tabIndex={-1}
        ref={domRef as React.RefObject<HTMLDivElement>}
        className={css.group}
      >
        {children}
      </div>
    </div>
  )
}

export interface FieldProps extends Control {
  children?: React.ReactNode
  onClear?: () => void
}

export const Field = ({
  domRef,
  aside,
  spread,
  disabled,
  readOnly,
  loading,
  required,
  error,
  label,
  icon: Icon,
  variant,
  className,
  style,
  children,
  onClear,
}: FieldProps) => {
  const icon = typeof Icon === "function" ? <Icon /> : Icon

  return (
    <div
      data-field
      data-disabled={disabled ? true : undefined}
      data-readonly={readOnly ? true : undefined}
      data-loading={loading ? true : undefined}
      data-error={error ? true : undefined}
      style={style}
      className={cl(css.field, variant && css[variant], className)}
      {...layout({ aside, spread })}
    >
      {label && (
        <label className={css.label} title={label}>
          {label}
          {required && " *"}
        </label>
      )}

      <div
        tabIndex={-1}
        ref={domRef as React.RefObject<HTMLDivElement>}
        className={css.control}
      >
        {children}

        {onClear && (
          <Button
            captive
            variant="icon"
            icon={Cross}
            action={onClear}
            tabIndex={-1}
            className={css.icon}
          />
        )}

        {(loading || error || icon) && (
          <div className={css.icon}>
            {loading ? (
              <Loader />
            ) : error ? (
              <AlertTriangle title={error} />
            ) : (
              icon
            )}
          </div>
        )}
      </div>
    </div>
  )
}
