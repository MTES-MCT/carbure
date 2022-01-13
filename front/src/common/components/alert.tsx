import React, { useState } from "react"
import cl from "clsx"

import styles from "./alert.module.css"
import { SystemProps } from "./index"
import { Loader } from "common-v2/components/icons"
import { Trans } from "react-i18next"

export const AlertLink = ({
  children,
  className,
  ...props
}: React.HTMLProps<HTMLSpanElement>) => (
  <span {...props} className={cl(styles.alertLink, className)}>
    {children}
  </span>
)

export type AlertProps = SystemProps &
  React.HTMLProps<HTMLDivElement> & {
    icon?: React.ComponentType
    level?: "warning" | "error" | "info"
    onClose?: (event: React.MouseEvent) => void
  }

export const Alert = ({
  level,
  icon: AlertIcon,
  children,
  className,
  ...props
}: AlertProps) => {
  const divClassName = cl(styles.alert, className, {
    [styles.alertWarning]: level === "warning",
    [styles.alertError]: level === "error",
    [styles.alertInfo]: level === "info",
  })

  return (
    <div {...props} className={divClassName}>
      {AlertIcon && <AlertIcon />}
      {children}
    </div>
  )
}

type AlertFilterProps = AlertProps & {
  loading?: boolean
  active?: boolean
  onActivate?: () => void
  onDispose?: () => void
}

export const AlertFilter = ({
  loading,
  children,
  active,
  icon,
  onActivate,
  onDispose,
  ...props
}: AlertFilterProps) => {
  const [open, setOpen] = useState(true)

  if (!open) {
    return null
  }

  return (
    <Alert
      {...props}
      icon={loading ? Loader : icon}
      className={cl(styles.alertFilter, loading && styles.alertLoading)}
    >
      {children}

      {onActivate &&
        onDispose &&
        (active ? (
          <AlertLink onClick={onDispose}>
            <Trans>Revenir à la liste complète</Trans>
          </AlertLink>
        ) : (
          <AlertLink onClick={onActivate}>
            <Trans>Voir la liste</Trans>
          </AlertLink>
        ))}

      <span
        className={cl(styles.alertLink, styles.alertClose)}
        onClick={() => {
          active && onDispose && onDispose()
          setOpen(false)
        }}
      >
        <Trans>Masquer ce message</Trans>
      </span>
    </Alert>
  )
}
