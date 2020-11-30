import React, { useCallback, useContext, useState } from "react"
import cl from "clsx"
import ReactDOM from "react-dom"

import styles from "./notifications.module.css"

import { Box } from "."
import { Cross } from "./icons"

const DEFAULT_TIMEOUT = 5000

const portal = document.getElementById("notifications")!

interface Notification {
  key: string
  level: "default" | "success" | "error" | "warning"
  text: string
  timeout: NodeJS.Timeout
}

interface NotificationsHook {
  list: Notification[]
  push: (n: {
    text: string
    duration?: number
    level?: Notification["level"]
  }) => void
  dispose: (k: string) => void
}

function useNotifications(): NotificationsHook {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const push: NotificationsHook["push"] = useCallback(
    ({ text, duration = DEFAULT_TIMEOUT, level = "default" }) => {
      const key = `${text}-${Date.now()}`

      // set auto close with timeout
      const timeout = setTimeout(() => {
        setNotifications((list) => list.filter((n) => n.key !== key))
      }, duration)

      const notification = { key, text, timeout, level }
      setNotifications((list) => [...list, notification])

      return notification
    },
    []
  )

  const dispose = useCallback((key: string) => {
    setNotifications((list) => {
      const notification = list.find((n) => n.key === key)

      if (notification) {
        clearTimeout(notification.timeout)
        return list.filter((n) => n.key !== key)
      }

      return list
    })
  }, [])

  return { list: notifications, push, dispose }
}

type NotificationsProps = {
  notifications: NotificationsHook
}

const Notifications = ({ notifications }: NotificationsProps) => {
  if (notifications.list.length === 0) {
    return null
  }

  return ReactDOM.createPortal(
    <Box as="ul" className={styles.notificationsWrapper}>
      {notifications.list.map((n, i) => (
        <Box
          as="li"
          row
          key={i}
          className={cl(
            styles.notification,
            n.level === "success" && styles.success,
            n.level === "warning" && styles.warning,
            n.level === "error" && styles.error
          )}
        >
          {n.text}
          <Cross
            title="Fermer la notification"
            onClick={() => notifications.dispose(n.key)}
          />
        </Box>
      ))}
    </Box>,
    portal
  )
}

const NotificationsContext = React.createContext<NotificationsHook>({
  list: [],
  push: () => {},
  dispose: () => {},
})

export function useNotificationContext() {
  return useContext(NotificationsContext)
}

type NotificationsProviderProps = {
  children: React.ReactNode
}

const NotificationsProvider = ({ children }: NotificationsProviderProps) => {
  const notifications = useNotifications()

  return (
    <React.Fragment>
      <NotificationsContext.Provider value={notifications}>
        {children}
      </NotificationsContext.Provider>
      <Notifications notifications={notifications} />
    </React.Fragment>
  )
}

export default NotificationsProvider
