import React from "react"
import ReactDOM from "react-dom"

import styles from "./confirm.module.css"

import { Title, Box, Button } from "."
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
  <Modal className={styles.confirm} onClose={onCancel}>
    <Title>{title}</Title>
    <p>{description}</p>

    <Box row className={styles.confirmButtons}>
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

export default confirm
