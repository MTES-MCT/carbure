import React from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import styles from "./dialog.module.css"

import { Title, Box } from "."
import { Button } from "./button"
import Modal from "./modal"
import NotificationsProvider from "./notifications"

type DialogProps = PromptProps<any> & {
  children: React.ReactNode
  className?: string
}

export const Dialog = ({ children, className, onResolve }: DialogProps) => (
  <Modal className={cl(styles.dialog, className)} onClose={() => onResolve()}>
    {children}
  </Modal>
)

export const DialogTitle = ({ text }: { text: string }) => <Title>{text}</Title>

export const DialogText = ({ text }: { text: string }) => (
  <span className={styles.dialogMessage}>{text}</span>
)

export const DialogButtons = (props: any) => (
  <Box {...props} row className={cl(props.className, styles.dialogButtons)} />
)

export type PromptProps<T> = {
  onResolve: (result?: T) => void
}

// return a promise that resolves only when the confirm or cancel button is clicked
export function prompt<T>(
  render: (resolve: (result?: T) => void) => React.ReactNode
  // form: React.ComponentType<PromptFormProps<T>>
): Promise<T | undefined> {
  return new Promise((resolve) => {
    const container = document.createElement("tmp")

    function onResolve(result?: T) {
      resolve(result)
      ReactDOM.unmountComponentAtNode(container)
    }

    // render component imperatively, outside of the regular react container
    ReactDOM.render(
      <NotificationsProvider>{render(onResolve)}</NotificationsProvider>,
      container
    )
  })
}

type ConfirmPromptProps = {
  title: string
  description: string
  onResolve: (result?: boolean) => void
}

const ConfirmPrompt = ({
  title,
  description,
  onResolve,
}: ConfirmPromptProps) => (
  <Dialog onResolve={onResolve}>
    <DialogTitle text={title} />
    <DialogText text={description} />

    <DialogButtons>
      <Button level="primary" onClick={() => onResolve(true)}>
        OK
      </Button>
      <Button onClick={() => onResolve(false)}>Annuler</Button>
    </DialogButtons>
  </Dialog>
)

export function confirm(title: string, description: string) {
  return prompt((resolve) => (
    <ConfirmPrompt
      title={title}
      description={description}
      onResolve={resolve}
    />
  )).then(Boolean)
}
