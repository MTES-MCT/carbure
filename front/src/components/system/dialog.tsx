import React, { useState } from "react"
import ReactDOM from "react-dom"

import styles from "./dialog.module.css"

import { Title, Box, Button, LabelInput } from "."
import Modal from "./modal"

type ConfirmProps = {
  title: string
  description: string
  onConfirm: () => void
  onCancel: () => void
}

export const Confirm = ({
  title,
  description,
  onConfirm,
  onCancel,
}: ConfirmProps) => (
  <Modal className={styles.dialog} onClose={onCancel}>
    <Title>{title}</Title>

    <span className={styles.dialogMessage}>{description}</span>

    <Box row className={styles.dialogButtons}>
      <Button level="primary" onClick={onConfirm}>
        OK
      </Button>
      <Button onClick={onCancel}>Annuler</Button>
    </Box>
  </Modal>
)

// return a promise that resolves only when the confirm or cancel button is clicked
export function confirm(title: string, description: string): Promise<boolean> {
  return new Promise((resolve) => {
    const container = document.createElement("tmp")

    function close(result: boolean) {
      resolve(result)
      ReactDOM.unmountComponentAtNode(container)
    }

    // render component imperatively, outside of the regular react container
    ReactDOM.render(
      <Confirm
        title={title}
        description={description}
        onConfirm={() => close(true)}
        onCancel={() => close(false)}
      />,
      container
    )
  })
}

type PromptProps = {
  title: string
  description: string
  onConfirm: (c: string) => void
  onCancel: () => void
}

export const Prompt = ({
  title,
  description,
  onConfirm,
  onCancel,
}: PromptProps) => {
  const [comment, setComment] = useState("")

  return (
    <Modal className={styles.dialog} onClose={onCancel}>
      <Title>{title}</Title>

      <span className={styles.dialogMessage}>{description}</span>

      <LabelInput
        label="Commentaire"
        value={comment}
        className={styles.promptInput}
        onChange={(e) => setComment(e.target.value)}
      />

      <Box row className={styles.dialogButtons}>
        <Button
          level="primary"
          disabled={!comment}
          onClick={() => onConfirm(comment)}
        >
          OK
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </Box>
    </Modal>
  )
}

// return a promise that resolves only when the confirm or cancel button is clicked
export function prompt(
  title: string,
  description: string
): Promise<string | undefined> {
  return new Promise((resolve) => {
    const container = document.createElement("tmp")

    function close(result?: string) {
      resolve(result)
      ReactDOM.unmountComponentAtNode(container)
    }

    // render component imperatively, outside of the regular react container
    ReactDOM.render(
      <Prompt
        title={title}
        description={description}
        onConfirm={(comment) => close(comment)}
        onCancel={() => close(undefined)}
      />,
      container
    )
  })
}
