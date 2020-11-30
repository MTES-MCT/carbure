import React, { useCallback, useState } from "react"
import ReactDOM from "react-dom"
import { Box } from "."
import { Cross } from "./icons"

import styles from "./notifications.module.css"

const DEFAULT_TIMEOUT = 5000

const portal = document.getElementById("notifications")!

interface Notification {
  key: string
  text: string
  timeout: NodeJS.Timeout
}

interface NotificationsHook {
  list: Notification[]
  push: (n: string, t?: number) => void
  dispose: (k: string) => void
}

function useNotifications(): NotificationsHook {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const push = useCallback(
    (text: string, duration: number = DEFAULT_TIMEOUT) => {
      const key = `${text}-${Date.now()}`

      // set auto close with timeout
      const timeout = setTimeout(() => {
        setNotifications((list) => list.filter((n) => n.key !== key))
      }, duration)

      const notification = { key, text, timeout }
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
      {notifications.list.map((notification, i) => (
        <Box as="li" row key={i} className={styles.notification}>
          {notification.text}
          <Cross
            title="Fermer la notification"
            onClick={() => notifications.dispose(notification.key)}
          />
        </Box>
      ))}
    </Box>,
    portal
  )
}

export const NotificationsContext = React.createContext<NotificationsHook>({
  list: [],
  push: () => {},
  dispose: () => {},
})

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
