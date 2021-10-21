import React from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import styles from "./dialog.module.css"

import { Title, Box } from "."
import { Button } from "./button"
import Modal from "./modal"
import NotificationsProvider from "./notifications"
import { Trans } from "react-i18next"
import Table, { TableProps } from "./table"

type DialogProps = PromptProps<any> & {
  children: React.ReactNode
  className?: string
  wide?: boolean
}

export const Dialog = ({
  children,
  className,
  wide = false,
  onResolve,
}: DialogProps) => (
  <Modal
    className={cl(styles.dialog, wide && styles.dialogWide, className)}
    onClose={() => onResolve()}
  >
    {children}
  </Modal>
)

type ContentProps = { text?: string; children?: React.ReactNode }

export const DialogTitle = ({ text, children }: ContentProps) => (
  <Title>{text ?? children}</Title>
)

export const DialogText = ({ text, children }: ContentProps) => (
  <span className={styles.dialogMessage}>{text ?? children}</span>
)

export const DialogSubtitle = ({ text, children }: ContentProps) => (
  <h2 className={styles.dialogSubtitle}>{text ?? children}</h2>
)

export function DialogTable<T>(props: TableProps<T>) {
  return (
    <Table {...props} className={cl(styles.dialogTable, props.className)} />
  )
}

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
        <Trans>Confirmer</Trans>
      </Button>
      <Button onClick={() => onResolve(false)}>
        <Trans>Annuler</Trans>
      </Button>
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
