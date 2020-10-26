import React, { useState } from "react"
import cl from "clsx"

import styles from "./alert.module.css"
import { SystemProps } from "./index"

// ALERT COMPONENT

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
  })

  return (
    <div {...props} className={divClassName}>
      {AlertIcon && <AlertIcon />}
      {children}
    </div>
  )
}

type AlertFilterProps = AlertProps & {
  active: boolean
  onActivate: () => void
  onDispose: () => void
}

export const AlertFilter = ({
  children,
  active,
  onActivate,
  onDispose,
  ...props
}: AlertFilterProps) => {
  const [open, setOpen] = useState(true)

  if (!open) {
    return null
  }

  return (
    <Alert {...props} className={styles.alertFilter}>
      {children}

      {active ? (
        <span className={styles.alertLink} onClick={onDispose}>
          Revenir à la liste complète
        </span>
      ) : (
        <span className={styles.alertLink} onClick={onActivate}>
          Voir la liste
        </span>
      )}

      <span
        className={cl(styles.alertLink, styles.alertClose)}
        onClick={() => {
          onDispose()
          setOpen(false)
        }}
      >
        Masquer ce message
      </span>
    </Alert>
  )
}
