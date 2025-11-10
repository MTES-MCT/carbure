import React, { useCallback, useEffect, useRef } from "react"
import cl from "clsx"
import { Cross } from "./icons"
import Button from "./button"
import { usePortal } from "./portal"
import css from "./notifications.module.css"
import { AxiosError } from "axios"
import { useTranslation } from "react-i18next"
import { HttpError } from "common/services/api-fetch"
import { useRoutes } from "common/hooks/routes"
import { Link } from "react-router"

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
  const routes = useRoutes()

  const DEFAULT_MESSAGE = (
    <>
      {t(
        "L'opération a échoué. Si le problème persiste, veuillez nous contacter depuis"
      )}{" "}
      <Link
        to={routes.CONTACT}
        style={{ textDecoration: "underline" }}
        target="_blank"
      >
        {t("ce formulaire")}
      </Link>
    </>
  )

  const getErrorText = (error: Error, defaultMessage?: React.ReactNode) => {
    let errorText: React.ReactNode = defaultMessage ?? DEFAULT_MESSAGE

    if (error instanceof AxiosError) {
      const errorCode = error.response?.data?.error
      if (errorCode) {
        const customErrorText = t(errorCode, { ns: "errors" })
        if (customErrorText !== errorCode) errorText = customErrorText
      }
    } else if (error instanceof HttpError) {
      if (error.data instanceof Object) {
        // Check if error.data is a record of <string, string[]>
        const isRecordOfStringArrays = Object.values(error.data).every(
          (value) => Array.isArray(value)
        )
        if (isRecordOfStringArrays) {
          errorText = <FormErrors errors={error.data} />
        } else if (typeof error.data.detail === "string") {
          errorText = error.data.detail
        }
      }
    }

    return errorText
  }

  const notifyError = useCallback((error?: Error, defaultMessage?: string) => {
    // If no error is provided, use the default message
    const errorText = error
      ? getErrorText(error, defaultMessage)
      : DEFAULT_MESSAGE
    return notify(errorText, { variant: "danger" })
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

export const FormErrors = ({
  errors,
}: {
  errors: Record<string, string[]>
}) => {
  const { t } = useTranslation()
  return (
    <ul>
      {Object.entries(errors).map(([field, fieldErrors]) => (
        <li key={field}>
          <b>{t(field, { ns: "fields" })}:</b> {fieldErrors.join(" ")}
        </li>
      ))}
    </ul>
  )
}

// initialize notification container and add it to the dom
const notifications = document.createElement("ul")
notifications.id = "notifications"
document.body.append(notifications)

export const DEFAULT_TIMEOUT = 10000
