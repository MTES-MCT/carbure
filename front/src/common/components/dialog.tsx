import React from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import styles from "./dialog.module.css"

import { Title, Box } from "."
import { Button } from "./button"
import Modal from "./modal"
import NotificationsProvider from "./notifications"

export const DialogButtons = (props: any) => (
  <Box {...props} row className={cl(props.className, styles.dialogButtons)} />
)

export type PromptFormProps<T> = {
  children?: React.ReactNode
  onConfirm: (c: T) => void
  onCancel: () => void
}

type PromptProps<T> = {
  title: string
  description: string
  form: React.ComponentType<PromptFormProps<T>>
  onConfirm: (c: T) => void
  onCancel: () => void
}

export function Prompt<T>({
  title,
  description,
  form: Form,
  onConfirm,
  onCancel,
}: PromptProps<T>) {
  return (
    <Modal className={styles.dialog} onClose={onCancel}>
      <Title>{title}</Title>
      {description && (
        <span className={styles.dialogMessage}>{description}</span>
      )}
      <Form onConfirm={onConfirm} onCancel={onCancel} />
    </Modal>
  )
}

// return a promise that resolves only when the confirm or cancel button is clicked
export function prompt<T>(
  title: string,
  description: string,
  form: React.ComponentType<PromptFormProps<T>>
): Promise<T | undefined> {
  return new Promise((resolve) => {
    const container = document.createElement("tmp")

    function close(result?: T) {
      resolve(result)
      ReactDOM.unmountComponentAtNode(container)
    }

    // render component imperatively, outside of the regular react container
    ReactDOM.render(
      <NotificationsProvider>
        <Prompt
          title={title}
          description={description}
          form={form}
          onConfirm={close}
          onCancel={() => close(undefined)}
        />
      </NotificationsProvider>,
      container
    )
  })
}

const ConfirmPrompt = ({ onConfirm, onCancel }: PromptFormProps<boolean>) => (
  <DialogButtons>
    <Button level="primary" onClick={() => onConfirm(true)}>
      OK
    </Button>
    <Button onClick={onCancel}>Annuler</Button>
  </DialogButtons>
)

export function confirm(title: string, description: string) {
  return prompt(title, description, ConfirmPrompt).then(Boolean)
}
