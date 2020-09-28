import React, { useState } from "react"
import { createPortal } from "react-dom"
import { Route, RouteProps, useHistory } from "react-router-dom"
import cl from "clsx"

import styles from "./modal.module.css"
import { Cross } from "../icons"

const root = document.getElementById("modal")!

export function useModal() {
  const [isOpen, setOpened] = useState(false)

  return {
    isOpen,
    open: () => setOpened(true),
    close: () => setOpened(false),
  }
}

type ModalProps = {
  className?: string
  children: React.ReactNode
  onClose?: (event: React.MouseEvent) => void
  [k: string]: any
}

const Modal = ({ className, onClose, children, ...props }: ModalProps) => {
  return createPortal(
    <div className={styles.modalWrapper}>
      <div className={styles.overlay} onClick={onClose} />
      <div {...props} className={cl(styles.modal, className)}>
        <Cross className={styles.closeModal} onClick={onClose} />
        {children}
      </div>
    </div>,
    root
  )
}

type ModalRouteProps = RouteProps & {
  back: string
}

export const ModalRoute = ({ children, back, ...props }: ModalRouteProps) => {
  const history = useHistory()

  return (
    <Route {...props}>
      <Modal onClose={() => history.push(back)}>{children}</Modal>
    </Route>
  )
}

export default Modal
