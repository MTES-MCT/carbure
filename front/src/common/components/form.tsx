import React from "react"

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
