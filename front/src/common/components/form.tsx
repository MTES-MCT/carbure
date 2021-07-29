import React from "react"
import cl from "clsx"
import { useTranslation } from "react-i18next"

import { FormChangeHandler } from "common/hooks/use-form"
import { Box, SystemProps } from "common/components"

import styles from "./form.module.css"

export type Field = {
  render: React.ComponentType<any>
  name: string
  [prop: string]: any
}

type FormFieldProps = {
  render: React.ComponentType<any>
  name: string
  [k: string]: any
}

export const FormField = ({ render: Render, ...props }: FormFieldProps) => {
  return <Render {...props} />
}

type FormGroupProps<T> = SystemProps & {
  readOnly?: boolean
  title?: React.ReactNode
  narrow?: boolean
  data: T
  errors?: Record<string, string>
  children: React.ReactNode
  onChange: FormChangeHandler<any>
}

export function FormGroup<T>({
  narrow,
  readOnly,
  title,
  children,
  data,
  errors = {},
  onChange,
  ...props
}: FormGroupProps<T>) {
  const { t } = useTranslation()

  return (
    <Box
      {...props}
      className={cl(styles.formGroup, narrow && styles.narrow, props.className)}
    >
      {title && <b className={styles.formGroupTitle}>{title}</b>}

      {React.Children.map(
        children,
        (child: any) =>
          child &&
          React.cloneElement(child, {
            readOnly: child.props.readOnly ?? readOnly,
            data,
            errors,
            onChange,
            t,
          })
      )}
    </Box>
  )
}

export const Form = ({
  onSubmit,
  ...props
}: React.HTMLProps<HTMLFormElement>) => {
  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    onSubmit && onSubmit(e)
  }

  return <form {...props} onSubmit={submit} />
}
