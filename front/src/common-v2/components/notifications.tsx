import React, { createContext, useCallback, useContext, useState } from "react"
import ReactDOM from "react-dom"
import cl from "clsx"
import { Cross } from "./icons"
import css from "./notifications.module.css"
import Button from "./button"

// initialize notification container and add it to the dom
const container = document.createElement("ul")
container.id = "notifications"
document.body.append(container)

export interface NotificationProviderProps {
  children: React.ReactNode
}

export const NotificationProvider = ({
  children,
}: NotificationProviderProps) => {
  const manager = useNotificationManager()
  return (
    <NotificationContext.Provider value={manager}>
      {children}
      <Notifications list={manager.notifications} />
    </NotificationContext.Provider>
  )
}

export const NotificationContext = createContext<
  NotificationManager | undefined
>(undefined)

export interface NotificationsProps {
  list: Notification[]
}

export const Notifications = ({ list }: NotificationsProps) => {
  if (list.length === 0) {
    return null
  }

  return ReactDOM.createPortal(
    <>
      {list.map(({ key, content, options, clear }, i) => (
        <li
          key={i}
          onClick={() => clearTimeout(key)}
          className={cl(
            css.notification,
            options?.variant && css[options.variant]
          )}
        >
          <span className={css.content}>{content}</span>
          <Button
            variant="icon"
            icon={Cross}
            action={clear}
            className={css.close}
          />
        </li>
      ))}
    </>,
    container
  )
}

export const DEFAULT_TIMEOUT = 10000

export type NotificationVariant = "info" | "success" | "warning" | "danger"

export interface NotificationOptions {
  variant?: NotificationVariant
  timeout?: number
}

export interface NotificationManager {
  notifications: Notification[]
  notify: Notifier
  clear: (key: number) => void
}

export function useNotificationManager() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const notify: Notifier = useCallback((content, options) => {
    function clear() {
      setNotifications((list) => list.filter((n) => n.key !== key))
    }

    // set auto close with timeout
    const key = window.setTimeout(clear, options?.timeout ?? DEFAULT_TIMEOUT)

    const notification = { key, content, options, clear }
    setNotifications((list) => [...list, notification])

    return notification
  }, [])

  const clear = useCallback((key: number) => {
    setNotifications((list) => {
      const notification = list.find((n) => n.key === key)

      if (notification) {
        notification.key && clearTimeout(notification.key)
        return list.filter((n) => n.key !== key)
      }

      return list
    })
  }, [])

  return { notifications, notify, clear }
}

export function useNotify() {
  const manager = useContext(NotificationContext)
  if (manager === undefined) {
    throw new Error("Notification context is not defined")
  }
  return manager.notify
}

export interface Notification {
  key: number
  content: React.ReactNode
  options?: NotificationOptions
  clear: () => void
}

type Notifier = (
  content: React.ReactNode,
  options?: NotificationOptions
) => Notification
