import React, { useEffect, useRef, useState } from "react"
import cl from "clsx"
import Button from "./button"
import {
  AlertTriangle,
  Cross,
  Loader,
  Search,
  Placeholder,
} from "common-v2/components/icons"
import { Col, layout, Layout, Overlay } from "./scaffold"
import { isInside } from "./dropdown"
import css from "./input.module.css"
import { useTranslation } from "react-i18next"

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
  title?: string
  icon?: React.FunctionComponent | React.ReactNode
  domRef?: React.RefObject<HTMLElement>
}

export interface TextInputProps extends Control {
  value?: string | undefined
  onChange?: (value: string | undefined) => void
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
    onChange={onChange ? (e) => onChange(e.target.value) : undefined}
    onClear={clear && value && onChange ? () => onChange(undefined) : undefined}
  />
)

export interface NumberInputProps extends Control {
  min?: number
  max?: number
  step?: number
  value?: number | undefined
  onChange?: (value: number | undefined) => void
}

export const NumberInput = ({
  clear,
  value,
  onChange,
  ...props
}: NumberInputProps) => (
  <Input
    {...props}
    type={props.readOnly ? "text" : "number"}
    value={value ?? ""}
    onClear={clear && value && onChange ? () => onChange(undefined) : undefined}
    onChange={
      !onChange
        ? undefined
        : (e) => {
            const value = parseFloat(e.target.value)
            const change = isNaN(value) ? undefined : value
            onChange(change)
          }
    }
  />
)

export interface DateInputProps extends Control {
  value?: string | undefined
  onChange?: (value: string | undefined) => void
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
    onChange={onChange ? (e) => onChange(e.target.value) : undefined}
    onClear={clear && value && onChange ? () => onChange(undefined) : undefined}
  />
)

export interface FileInputProps extends Control {
  value?: File | undefined
  onChange?: (value: File | undefined) => void
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
    type="file"
    onClear={clear && value && onChange ? () => onChange(undefined) : undefined}
  >
    <label tabIndex={0} className={css.file}>
      <input
        hidden
        disabled={props.disabled}
        readOnly={props.readOnly}
        required={props.required}
        name={props.name}
        type="file"
        onChange={onChange ? (e) => onChange(e.target.files?.[0]) : undefined}
      />
      {value?.name ?? placeholder}
    </label>
  </Field>
)

export interface FileAreaProps {
  className?: string
  style?: React.CSSProperties
  children?: React.ReactNode
  label?: string
  icon?: React.FunctionComponent | React.ReactNode
  value?: File | undefined
  onChange?: (value: File | undefined) => void
}

export const FileArea = ({
  children,
  icon: Icon,
  label,
  onChange,
  ...props
}: FileAreaProps) => {
  const [active, setActive] = useState(false)
  const icon = typeof Icon === "function" ? <Icon /> : Icon

  return (
    <div
      {...props}
      data-active={active ? true : undefined}
      onDragOver={(e) => {
        e.preventDefault()
        if (!active && e.dataTransfer.types.includes("Files")) {
          setActive(true)
        }
      }}
      onDragLeave={(e) => {
        e.preventDefault()
        if (!isInside(e.currentTarget, e.relatedTarget)) {
          setActive(false)
        }
      }}
      onDrop={(e) => {
        e.preventDefault()
        if (e.dataTransfer.files.length > 0) {
          onChange?.(e.dataTransfer.files[0])
          setActive(false)
        }
      }}
    >
      {children}
      {active && (
        <Overlay>
          <Col className={css.fileplaceholder}>
            {icon}
            {label}
          </Col>
        </Overlay>
      )}
    </div>
  )
}

export interface InputProps extends Control {
  min?: number
  max?: number
  step?: number
  value: string | number | undefined
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  onClear?: () => void
}

export const Input = ({
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
      type={props.type}
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
  const { t } = useTranslation()

  const timeoutRef = useRef<number>()
  const [search, setSearch] = useState(value ?? "")

  useEffect(() => {
    setSearch(value ?? "")
  }, [value])

  function debouncedSearch(search: string) {
    if (!debounce) return onChange?.(search)

    setSearch(search)
    timeoutRef.current && window.clearTimeout(timeoutRef.current)
    timeoutRef.current = window.setTimeout(() => onChange?.(search), debounce)
  }

  return (
    <Field
      {...props}
      className={cl(css.search, className)}
      onClear={
        clear && search && onChange ? () => onChange(undefined) : undefined
      }
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
        placeholder={placeholder ?? t("Rechercher...")}
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
  asideX,
  asideY,
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
      {...layout({ asideX, asideY, spread })}
    >
      {label && (
        <label className={css.label} title={label}>
          {label}
          {required && !(disabled || readOnly) && " *"}
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
  asideX,
  asideY,
  spread,
  disabled,
  readOnly,
  loading,
  required,
  type,
  error,
  label,
  icon: Icon,
  variant,
  title,
  className,
  style,
  children,
  onClear,
}: FieldProps) => (
  <div
    data-field
    data-disabled={disabled ? true : undefined}
    data-readonly={readOnly ? true : undefined}
    data-loading={loading ? true : undefined}
    data-error={error ? true : undefined}
    title={title}
    style={style}
    className={cl(css.field, variant && css[variant], className)}
    {...layout({ asideX, asideY, spread })}
  >
    {label && (
      <label className={css.label} title={title ?? label}>
        {label}
        {required && !(disabled || readOnly) && " *"}
      </label>
    )}

    <div
      tabIndex={-1}
      data-interactive={isInteractive(type) ? true : undefined}
      ref={domRef as React.RefObject<HTMLDivElement>}
      className={css.control}
    >
      {children}

      {!disabled && !readOnly && onClear && (
        <Button
          captive
          variant="icon"
          icon={Cross}
          action={onClear}
          tabIndex={-1}
          className={css.icon}
        />
      )}

      <div className={css.icon}>
        {loading === true ? (
          <Loader passthrough />
        ) : error ? (
          <AlertTriangle title={error} />
        ) : typeof Icon === "function" ? (
          <Icon />
        ) : Icon !== undefined ? (
          Icon
        ) : loading === false ? (
          <Placeholder />
        ) : null}
      </div>
    </div>
  </div>
)

function isInteractive(type: string | undefined) {
  return type === "button" || type === "file"
}
