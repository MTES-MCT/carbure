import React, { useCallback, useContext, useState } from "react"
import cl from "clsx"
import { identity } from "common-v2/utils/normalizers"
import css from "./form.module.css"

export type FormVariant = "inline" | "complex"

export interface FormProps<T> {
  id?: string
  className?: string
  style?: React.CSSProperties
  children: React.ReactNode
  variant?: FormVariant
  form?: FormManager<T>
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
}: FormProps<T>) {
  return (
    <FormContext.Provider value={form}>
      <form
        id={id}
        className={cl(css.form, variant && css[variant], className)}
        style={style}
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
  bind: Bind<T>
  setField: FieldSetter<T>
  setValue: React.Dispatch<React.SetStateAction<T>>
}

export interface FormOptions<T> {
  setValue?: (nextState: T, prevState?: T) => T
}

export function useForm<T>(
  initialState: T,
  options?: FormOptions<T>
): FormManager<T> {
  const [value, setValue] = useState(initialState)
  const mutate = options?.setValue ?? identity

  const setField = useCallback(
    (name: keyof T, value: T[keyof T]) => {
      setValue((form) => mutate({ ...form, [name]: value }, form))
    },
    [mutate]
  )

  const bind = useBindCallback(value, setField)

  return { value, bind, setField, setValue }
}

export function useBind<T>() {
  const form = useFormContext<T>()
  return useBindCallback<T>(form.value, form.setField)
}

export function useBindCallback<T>(
  value: T,
  setField: (name: keyof T, value: T[keyof T]) => void
): Bind<T> {
  return useCallback(
    (name, option) => ({
      name,
      value: option ?? value[name],
      checked: option ? option === value[name] : undefined,
      onChange: (value) => setField(name, value),
    }),
    [value, setField]
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
  onChange: (value: T[N]) => void
  checked?: boolean
}

export type FieldSetter<T> = (name: keyof T, value: T[keyof T]) => void

export default Form
