import React, { useContext, useEffect, useRef } from "react"
import ReactDOM from "react-dom"
import cl from "clsx"
import { Cross } from "common-v2/components/icons"
import Button from "./button"
import { PortalContext } from "./portal"
import css from "./notifications.module.css"

export type Notifier = (
  content: React.ReactNode,
  options?: NotificationOptions
) => void
export interface NotificationOptions {
  variant?: NotificationVariant
  timeout?: number
}

export function useNotify(): Notifier {
  const manager = useContext(PortalContext)
  if (manager === undefined) {
    throw new Error("Notification context is not defined")
  }
  return (content, options) =>
    manager.portal((close) => (
      <Notification content={content} options={options} onClose={close} />
    ))
}

export type NotificationVariant = "info" | "success" | "warning" | "danger"

export interface NotificationProps {
  content: React.ReactNode
  options?: NotificationOptions
  onClose: () => void
}

export const Notification = ({
  content,
  options,
  onClose,
}: NotificationProps) => {
  const timeoutRef = useRef<number>()

  useEffect(() => {
    timeoutRef.current = window.setTimeout(onClose, DEFAULT_TIMEOUT)
    return () => window.clearTimeout(timeoutRef.current)
  }, [timeoutRef, onClose])

  return ReactDOM.createPortal(
    <li
      onClick={() => window.clearTimeout(timeoutRef.current)}
      className={cl(css.notification, options?.variant && css[options.variant])}
    >
      <span className={css.content}>{content}</span>
      <Button
        variant="icon"
        icon={Cross}
        action={onClose}
        className={css.close}
      />
    </li>,
    notifications
  )
}

// initialize notification container and add it to the dom
const notifications = document.createElement("ul")
notifications.id = "notifications"
document.body.append(notifications)

export const DEFAULT_TIMEOUT = 10000
