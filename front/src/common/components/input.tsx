import React, { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import Button from "./button"
import {
  AlertTriangle,
  Cross,
  Loader,
  Search,
  Placeholder,
  InfoCircle,
} from "./icons"
import { Col, layout, Layout, Overlay } from "./scaffold"
import { isInside } from "./dropdown"
import css from "./input.module.css"
import i18next from "i18next"
import Tooltip from "./tooltip"

export type FieldVariant = "outline" | "solid" | "inline" | "text"

export interface Control extends Layout {
  className?: string
  style?: React.CSSProperties
  autoFocus?: boolean
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
  rightContent?: React.ReactNode
  hasTooltip?: boolean
  domRef?: React.RefObject<HTMLElement>
}

export interface TextInputProps extends Control {
  value?: string | undefined
  autoComplete?: boolean
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

export interface FileListInputProps extends Control {
  value?: FileList
  onChange?: (value: FileList | undefined) => void
}

export const FileListInput = ({
  clear,
  placeholder = i18next.t("Selectionner des fichiers"),
  value,
  autoFocus,
  onChange,
  ...props
}: FileListInputProps) => (

  <FileInputField
    value={value}
    onChange={onChange ? (e) => onChange(e?.target.files ?? undefined) : undefined}
    multiple={true}
    placeholder={value?.[0]?.name ?? placeholder}
    {...props}
  />
)

export interface FileInputProps extends Control {
  value?: File | undefined
  onChange?: (value: File | undefined) => void
}

export const FileInput = ({
  clear,
  placeholder = i18next.t("Selectionner un fichier"),
  value,
  autoFocus,
  onChange,
  ...props
}: FileInputProps) => {
  return <FileInputField
    value={value}
    onChange={(e) => onChange ? onChange(e?.target.files?.[0]) : undefined}
    multiple={false}
    placeholder={value?.name ?? placeholder}
    {...props}
  />
}


export interface FileInputFieldProps extends Control {
  value?: File | FileList | undefined
  onChange?: (e?: React.ChangeEvent<HTMLInputElement>) => void
  multiple?: boolean
}
export const FileInputField = ({
  clear,
  placeholder = i18next.t("Selectionner un fichier"),
  value,
  multiple = false,
  onChange,
  ...props
}: FileInputFieldProps) => {
  const { t } = useTranslation()
  const inputRef = useRef<HTMLInputElement>(null)
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!inputRef.current) return
    var files = e.target.files;

    if (files === null) return

    for (var i = 0; i < files.length; i++) {
      if (files[i].size > 5000000) {
        console.log('files[i]:', files[i])
        const message = t(
          "La taille du fichier \"{{fileName}}\" est trop importante pour être analysée (5mo maximum).", { fileName: files[i].name }
        )
        inputRef.current.setCustomValidity(message)
        inputRef.current.reportValidity()
        return
      }
    }

    return onChange ? onChange(e) : undefined
  }

  return <Field
    {...props}
    type="file"
    onClear={clear && value && onChange ? () => onChange(undefined) : undefined}
  >
    <label className={css.file}>
      <input
        ref={inputRef}
        autoFocus={props.autoFocus}
        disabled={props.disabled}
        readOnly={props.readOnly}
        required={props.required}
        multiple={multiple}
        name={props.name}
        style={{ opacity: 0, position: "absolute" }}
        type="file"
        onChange={handleChange}
      />
      {placeholder}
    </label>
  </Field>
}

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
  autoComplete?: boolean
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
  autoComplete,
  autoFocus,
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
      autoFocus={autoFocus}
      autoComplete={!autoComplete ? "off" : undefined}
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
  autoFocus,
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
      autoFocus={autoFocus}
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
  autoFocus,
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
      <div className={css.searchIcon}>
        <Search />
      </div>

      <input
        title={search}
        autoFocus={autoFocus}
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
  rightContent,
  variant,
  title,
  className,
  style,
  children,
  onClear,
  hasTooltip,
}: FieldProps) => {
  const icon =
    loading === true ? (
      <Loader passthrough />
    ) : typeof Icon === "function" ? (
      <Icon />
    ) : Icon !== undefined ? (
      Icon
    ) : error ? (
      <AlertTriangle title={error} />
    ) : loading === false ? (
      <Placeholder />
    ) : null

  const TooltipWrapper = ({ children }: { children: React.ReactNode }) => {
    if (hasTooltip) {
      return (
        <Tooltip title={title ?? label!}>
          {children}
          <InfoCircle
            color="#a4a4a4"
            size={13}
            style={{
              margin: "7px 0px 0 2px",
              position: "absolute",
            }}
          />
        </Tooltip>
      )
    }
    return <>{children}</>
  }

  return (
    <div
      data-field
      data-disabled={disabled ? true : undefined}
      data-readonly={readOnly ? true : undefined}
      data-loading={loading ? true : undefined}
      data-error={error ? true : undefined}
      title={hasTooltip ? "" : title}
      style={style}
      className={cl(css.field, variant && css[variant], className)}
      {...layout({ asideX, asideY, spread })}
    >
      {label && (
        <TooltipWrapper>
          <label className={css.label} title={hasTooltip ? "" : title ?? label}>
            {label}
            {required && !(disabled || readOnly) && " *"}
          </label>
        </TooltipWrapper>
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

        {icon && <div className={css.icon}>{icon}</div>}
        {!!rightContent && rightContent}
      </div>
    </div>
  )
}

function isInteractive(type: string | undefined) {
  return type === "button" || type === "file"
}

export function BlankField() {
  return <div className={css.blankField} />
}
