import React, { useCallback, useContext, useState } from "react"
import cl from "clsx"
import css from "./form.module.css"

export type FormVariant = "inline" | "columns"

export interface FormProps<T> {
  id?: string
  className?: string
  style?: React.CSSProperties
  children: React.ReactNode
  variant?: FormVariant
  form?: FormManager<T>
  novalidate?: boolean
  onSubmit?: (
    value: T | undefined,
    e?: React.FormEvent<HTMLFormElement>
  ) => void
}

export function Form<T>({
  id,
  className,
  style,
  variant,
  form,
  children,
  onSubmit,
  novalidate,
}: FormProps<T>) {
  return (
    <FormContext.Provider value={form}>
      <form
        id={id}
        className={cl(css.form, variant && css[variant], className)}
        style={style}
        noValidate={novalidate}
        onSubmit={(e) => {
          e.preventDefault()
          onSubmit?.(form?.value, e)
        }}
      >
        {children}
      </form>
    </FormContext.Provider>
  )
}

export interface FieldsetProps {
  className?: string
  style?: React.CSSProperties
  small?: boolean
  children?: React.ReactNode
  label?: string
}

export const Fieldset = ({
  className,
  style,
  small,
  label,
  children,
}: FieldsetProps) => (
  <fieldset
    className={cl(css.fieldset, small && css.small, className)}
    style={style}
  >
    {label && <legend title={label}>{label}</legend>}
    {children}
  </fieldset>
)

export interface FormManager<T> {
  value: T
  errors: FormErrors<T>
  bind: Bind<T>
  setField: FieldSetter<T>
  setFieldError: (name: keyof T, error: string | undefined) => void
  setDisabledFields: (fieldsNames: string[]) => void
  clearDisabledFields: () => void
  setValue: React.Dispatch<React.SetStateAction<T>>
}

export type FormErrors<T> = Partial<Record<keyof T, string>>
export type FormDisabledFields<T> = Partial<Record<keyof T, boolean>>

const EMPTY_ERRORS: FormErrors<any> = {}
const EMPTY_DISABLED_FIELDS: FormDisabledFields<any> = {}

function identity<T>(value: T) {
  return value
}

export interface FormOptions<T> {
  errors?: FormErrors<T>
  setValue?: (nextState: T, prevState?: T) => T
}

export function useForm<T>(
  initialState: T,
  options?: FormOptions<T>
): FormManager<T> {
  const [value, setValue] = useState(initialState)
  const [_errors, setErrors] = useState(EMPTY_ERRORS)
  const [disabledFields, _setDisabledFields] = useState(EMPTY_DISABLED_FIELDS)

  const errors = options?.errors ?? _errors
  const mutate = options?.setValue ?? identity

  const setField = useCallback(
    (name: keyof T, value: T[keyof T]) => {
      setValue((form) => mutate({ ...form, [name]: value }, form))
      setFieldError(name, undefined)
    },
    [mutate]
  )

  const setFieldError = useCallback(
    (name: keyof T, error: string | undefined) => {
      setErrors((errors) => ({ ...errors, [name]: error }))
    },
    []
  )

  const clearDisabledFields = useCallback(() => {
    _setDisabledFields(EMPTY_DISABLED_FIELDS)
  }, [])

  const setDisabledFields = useCallback(
    (fieldsNames: string[]) => {
      const fields = { ...disabledFields }
      fieldsNames.forEach((name) => {
        fields[name] = true
      })
      _setDisabledFields(fields)
    },
    [disabledFields]
  )

  const bind = useBindCallback(value, errors, disabledFields, setField)

  return {
    value,
    errors,
    setFieldError,
    setDisabledFields,
    clearDisabledFields,
    bind,
    setField,
    setValue,
  }
}

export function useBind<T>() {
  const form = useFormContext<T>()
  return form.bind
}

export function useBindCallback<T>(
  value: T,
  errors: FormErrors<T>,
  disabledFields: FormDisabledFields<T>,
  setField: (name: keyof T, value: T[keyof T]) => void
): Bind<T> {
  return useCallback(
    (name, option) => ({
      name,
      value: option ?? value[name],
      disabled: disabledFields[name],
      checked: option ? option === value[name] : undefined,
      error: errors[name],
      onChange: (value) => setField(name, value),
    }),
    [value, errors, setField, disabledFields]
  )
}

export function useFormContext<T>() {
  const form = useContext<FormManager<T> | undefined>(FormContext)
  if (form === undefined) throw new Error("Form context is not defined")
  return form
}

export const FormContext = React.createContext<FormManager<any> | undefined>(
  undefined
)

export type Bind<T> = <N extends keyof T>(
  name: N,
  option?: T[N]
) => BindProps<T, N>

export interface BindProps<T, N extends keyof T> {
  name: N
  value: T[N]
  error: string | undefined
  checked: boolean | undefined
  onChange: (value: T[N]) => void
}

export type FieldSetter<T> = (name: keyof T, value: T[keyof T]) => void

export default Form
