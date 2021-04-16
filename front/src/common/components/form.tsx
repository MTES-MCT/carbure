import React from "react"
import cl from "clsx"

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

type FormGroupProps = SystemProps & {
  readOnly?: boolean
  title?: string
  disabled?: boolean
  narrow?: boolean
  fieldErrors?: Record<string, any>
  children: React.ReactNode
  onChange: FormChangeHandler<any>
}

export const FormGroup = ({
  narrow,
  readOnly,
  title,
  children,
  onChange,
  ...props
}: FormGroupProps) => {
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
            onChange: onChange,
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
