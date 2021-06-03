import React, { useState } from "react"
import cl from "clsx"

import styles from "./alert.module.css"
import { Box, SystemProps, Title } from "./index"
import { ChevronDown, Loader } from "./icons"
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

type CollapsibleProps = AlertProps & {
  title: string
  open?: boolean
}

export const Collapsible = ({
  title,
  icon: CollapsibleIcon,
  children,
  className,
  open = false,
  ...props
}: CollapsibleProps) => {
  const [collasped, setCollapsed] = useState(!open)

  return (
    <Alert {...props} className={cl(styles.collapsibleAlert, className)}>
      <Box
        row
        onClick={() => setCollapsed(!collasped)}
        className={styles.collapsibleBar}
      >
        {CollapsibleIcon && <CollapsibleIcon />}
        <Title className={styles.collapsibleTitle}>{title}</Title>
        <ChevronDown className={styles.collapsibleArrow} />
      </Box>

      {!collasped && (
        <Box className={styles.collapsibleDetails}>{children}</Box>
      )}
    </Alert>
  )
}
