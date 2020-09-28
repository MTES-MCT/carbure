import React, { useState } from "react"
import { createPortal } from "react-dom"
import cl from "clsx"

import styles from "./modal.module.css"
import { Cross } from "./icons"

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

export default Modal
