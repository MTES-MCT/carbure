import React, { useEffect } from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import styles from "./modal.module.css"

import { Cross } from "./icons"

const portal = document.getElementById("modal")!

type ModalProps = {
  className?: string
  children: React.ReactNode
  onClose: () => void
  [k: string]: any
}

const Modal = ({ className, onClose, children, ...props }: ModalProps) => {
  useEffect(() => {
    function onEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose()
      }
    }

    window.addEventListener("keydown", onEscape)
    return () => window.removeEventListener("keydown", onEscape)
  }, [onClose])

  return ReactDOM.createPortal(
    <div className={styles.modalWrapper}>
      <div className={styles.overlay} onClick={onClose} />
      <div {...props} className={cl(styles.modal, className)}>
        <Cross className={styles.closeModal} onClick={onClose} />
        {children}
      </div>
    </div>,
    portal
  )
}

export default Modal
