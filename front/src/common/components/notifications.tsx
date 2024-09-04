import React, { useCallback, useEffect, useRef } from "react"
import cl from "clsx"
import { Cross } from "./icons"
import Button from "./button"
import { usePortal } from "./portal"
import css from "./notifications.module.css"
import { AxiosError } from "axios"
import { useTranslation } from "react-i18next"

export type Notifier = (
  content: React.ReactNode,
  options?: NotificationOptions
) => void
export interface NotificationOptions {
  variant?: NotificationVariant
  timeout?: number
}

export function useNotify(): Notifier {
  const portal = usePortal(notifications)
  return (content, options) =>
    portal((close) => (
      <Notification content={content} options={options} onClose={close} />
    ))
}

export function useNotifyError() {
  const { t } = useTranslation()
  const notify = useNotify()

  const getErrorText = (error: Error, defaultMessage?: string) => {
    const errorCode = (error as AxiosError<{ error: string }>).response?.data
      .error

    let errorText =
      defaultMessage ||
      t("La demande a échoué. Réessayez ou contactez carbure@beta.gouv.fr")
    if (errorCode) {
      const customErrorText = t(errorCode, { ns: "errors" })
      if (customErrorText !== errorCode) errorText = customErrorText
    }

    return errorText
  }

  const notifyError = useCallback((error: Error, defaultMessage?: string) => {
    return notify(getErrorText(error, defaultMessage), { variant: "danger" })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return notifyError
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

  return (
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
    </li>
  )
}

// initialize notification container and add it to the dom
const notifications = document.createElement("ul")
notifications.id = "notifications"
document.body.append(notifications)

export const DEFAULT_TIMEOUT = 10000
